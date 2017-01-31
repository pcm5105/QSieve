#include <ArduinoJson.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <FS.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include <climits>
#include <vector>

const uint16_t CLICK_DELAY = 500;
const uint16_t HEADER_BYTES = 551;
const uint16_t HOLD_LENGTH = 1000;
const uint8_t DOUBLE_CLICK = 1;
const uint8_t HOLD_CLICK = 2;
const uint8_t INVALID_CLICK = 3;
const uint8_t SINGLE_CLICK = 0;
const uint8_t GPIO_PIN = 13;
const uint16_t PORTAL_TIMEOUT = 600;

char groupMeToken[41] = {'\0'};
char groupMessages[3][141] = {'\0'};
unsigned long currentTime;
uint32_t groupIds[3] = {0};
unsigned long prevStartTime = 0;
unsigned long startTime = 0;
uint8_t clickType = INVALID_CLICK;
bool pinChanged = false;

bool writeConfigFile();
bool readConfigFile();
void setupWiFiManager();

void setup()
{
	Serial.begin(115200);
	SPIFFS.begin();
	readConfigFile();
	// This ensures that the button press pulls the pin low and that the button
	// release pulls it back high.
	pinMode(GPIO_PIN, INPUT_PULLUP);
	// Check if any of the required fields need to be added to the user for the
	// device to function correctly
	if (digitalRead(GPIO_PIN) == LOW || WiFi.SSID() == "" || groupMeToken[0] == '\0' || groupIds[0] == 0 || groupMessages[0][0] == '\0')
	{
		setupWiFiManager();
	}
	else
	{
		WiFi.mode(WIFI_STA);
		int connRes = WiFi.waitForConnectResult();
	}

	if (WiFi.status() != WL_CONNECTED)
	{
		setupWiFiManager();
	}

	SPIFFS.end();
}

void loop()
{
	// Button released
	if (pinChanged && digitalRead(GPIO_PIN) == HIGH)
	{
		pinChanged = false;

		if (clickType != DOUBLE_CLICK && prevStartTime != 0 && startTime -
				prevStartTime <= CLICK_DELAY)
		{
			clickType = DOUBLE_CLICK;
		}
		else if (clickType != SINGLE_CLICK && millis() - startTime <= CLICK_DELAY)
		{
			clickType = SINGLE_CLICK;
		}

		delay(5);
	}
	// Button pressed
	else if (!pinChanged && clickType != HOLD_CLICK && digitalRead(GPIO_PIN) == LOW)
	{
		pinChanged = true;
		clickType = HOLD_CLICK;
		prevStartTime = startTime;
		startTime = millis();
	}
	currentTime = millis();

	// TODO: I could probably combine these if statements into one
	if (clickType == DOUBLE_CLICK)
	{
		sendMessage(clickType);
		clickType = INVALID_CLICK;
	}
	else if (clickType == SINGLE_CLICK && currentTime - startTime > CLICK_DELAY)
	{
		sendMessage(clickType);
		clickType = INVALID_CLICK;
	}
	else if (clickType == HOLD_CLICK && currentTime - startTime > HOLD_LENGTH)
	{
		sendMessage(clickType);
		clickType = INVALID_CLICK;
	}
}

void sendMessage(uint8_t clickType)
{
	const char FINGERPRINT[] = "ED:22:CB:A5:30:A8:BB:B0:C2:27:93:90:65:CD:64:EA:EA:18:3F:0E";
	const char SERVER[] = "api.groupme.com";
	const uint16_t HTTPS_PORT = 443;
	char uid[11];
	char groupIdStr[48] = {'\0'};
	WiFiClientSecure client;

	if (client.connect(SERVER, HTTPS_PORT))
	{
		if (client.verify(FINGERPRINT, SERVER))
		{
			sprintf(groupIdStr, "%u", groupIds[clickType]);
			sprintf(uid, "%u", random(UINT_MAX));
			// Length of POST data (I believe):
			// 11 + 15 + 10 + 2 + 8 + 140 + 1 + 2 + 1

			// Length of request:
			// 16 + 8 + 16 + 40 + 9 + 1

			// Send the request
			client.print("POST /v3/groups/");
			client.print(groupIdStr);
			client.print("/messages?token=");
			client.print(groupMeToken);
			client.println(F(" HTTP/1.1"));

			client.println("Host: api.groupme.com");
			client.println("Content-Type: application/json");
			client.print("Content-Length: ");
			client.println(40 + strlen(uid) +
					strlen(groupMessages[clickType]));
			client.println();
			client.print("{\"message\":{\"source_guid\":\"");
			client.print(uid);
			client.print("\",\"text\":\"");
			client.print(groupMessages[clickType]);
			client.println("\"}}");
			client.println();
			long timeOut = 4000;
			long lastTime = millis();

			while ((millis() - lastTime) < timeOut)
			{
				while (client.available())
				{
					char c = client.read();
					Serial.write(c);
				}
			}
		}
	}

	// Sleep indefinitely
	ESP.deepSleep(0);
}

bool readConfigFile()
{
	File f = SPIFFS.open("/token", "r");
	if (f)
	{
		const size_t size = f.size();
		std::unique_ptr<char[]> buf(new char[size]);
		f.readBytes(buf.get(), size);
		f.close();
		DynamicJsonBuffer jsonBuffer;
		JsonObject& root = jsonBuffer.parseObject(buf.get());

		if (!root.success())
		{
			return false;
		}
		else
		{
			root.prettyPrintTo(Serial);

			if (root.containsKey("token"))
			{
				strcpy(groupMeToken, root["token"]);
			}
			if (root.containsKey("ids"))
			{
				root["ids"].asArray().copyTo(groupIds);
			}
			if (root.containsKey("messages"))
			{
				// Must not be possible to get strings in an array
				for (uint8_t i = 0; i < 3; i++)
				{
					strcpy(groupMessages[i], root["messages"][i]);
				}
			}
		}
	}
	else
	{
		return false;
	}
	return true;
}

bool writeConfigFile()
{
	File f = SPIFFS.open("/token", "w+");
	StaticJsonBuffer<16 + 3 * (140 + 8)> jsonBuffer;
	JsonObject &root = jsonBuffer.createObject();

	root["token"] = groupMeToken;
	JsonArray &arrIds = root.createNestedArray("ids");

	for (uint8_t i = 0; i < 3; i++)
	{
		arrIds.add(groupIds[i]);
	}

	JsonArray &arrMsgs = root.createNestedArray("messages");

	for (uint8_t i = 0; i < 3; i++)
	{
		arrMsgs.add(groupMessages[i]);
	}

	// Add other options to the config file
	if (f)
	{
		root.printTo(f);
		root.prettyPrintTo(Serial);
		f.close();
	}
}

void setupWiFiManager()
{
	char groupUrl[48] = {'\0'};
	WiFiManager wifiManager;
	wifiManager.setDebugOutput(false);
	// Add the groups ids
	WiFiManagerParameter paramGroupToken("g_toke", "GroupMe Token", groupMeToken, 41);
	wifiManager.addParameter(&paramGroupToken);
	std::vector<WiFiManagerParameter> paramGroupIds;
	std::vector<WiFiManagerParameter> paramGroupMsgs;
	paramGroupIds.reserve(3);
	paramGroupMsgs.reserve(3);
	char groupIdStr[3][48] = {'\0'};
	char htmlId[6][4] = {'\0'};

	for (uint8_t i = 0; i < 3; i++)
	{
		sprintf(groupIdStr[i], "%u", groupIds[i]);
		sprintf(htmlId[i], "g_%u", i);
		paramGroupIds.push_back(WiFiManagerParameter(htmlId[i], "GroupMe URL", groupIdStr[i], 48));
		wifiManager.addParameter(&paramGroupIds[i]);
		sprintf(htmlId[i + 3], "m_%u", i);
		paramGroupMsgs.push_back(WiFiManagerParameter(htmlId[i + 3], "Message", groupMessages[i], 141));
		wifiManager.addParameter(&paramGroupMsgs[i]);
	}

	wifiManager.setConfigPortalTimeout(PORTAL_TIMEOUT);
	wifiManager.startConfigPortal();
	strcpy(groupMeToken, paramGroupToken.getValue());

	for (uint8_t i = 0; i < 3; i++)
	{
		strcpy(groupUrl, paramGroupIds[i].getValue());
		strcpy(groupMessages[i], paramGroupMsgs[i].getValue());

		for (uint8_t j = 0; j < 141; j++)
		{
			if ((groupIds[i] = strtol(groupUrl + j, NULL, 10)) ||
				(groupIds[i] = strtol(groupUrl + j, NULL, 10)))
			{
				break;
			}
		}
	}

	writeConfigFile();
}
