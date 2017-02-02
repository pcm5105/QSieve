#imports
import math


#The number to factor is n = 135291536006657
#Bressoud's number is 4999486012441

#First we must define our sieving interval:

#N = 4999486012441

#initially N  = 4999486012441, M = 5000, B = 30
###################### Quadratic Sieve Function (Main) ####################       
def QSieve(N,M,B):

        
        Base = getFactorBase(N,M,B)  
        print("Printing session without outputs")                                                           #get the factor base
        print("Printing Factor Base: ")                             
        #print(Base)                                                 #then print it         
        print("\n")

        Solutions = []                                              #create a empty list
        for i in range(B-1):                                        #to hold tonelli solutions 
                Solutions.append(0)
     
        i = 0                                                        
        if Base[0] == 2:                                            #if the first prime in the base is a 2
            Solutions[0] = 0                                        #the first index in solutions is set to zero                                                             #this is because tonelli's can't do 2 
            i = i + 1                                               #go to the next i 
            
    
        while i < B-1:                                              #while we're not at the end of our factor base                                                         
            Solutions[i] = tonelli(N,Base[i])                       #calculate tonelli's of this spot 
            i = i + 1                                               #do this for all primes in factor base
                
        print("Printing Matrix of Tonelli Solutions: ")             #now we have our tonelli solutions matrix 
        #print(Solutions)                                            #so print it 
        print("\n")                             
        

        zeroMatrix = [[0 for x in range(B)] for y in range(2*M)]    #create a matrix of all zeros size Bx2M B = col                           
                   
        j = 0                                                       #j counts our columns 
        while j < B-1:                                              #while we still have columns to go over 
            i = 0                                                   #i counts our rows 
            while i < (2*M):                                        #while we still have rows to go over
                                                 
                                                                    #if ri = +- ti mod P

                if Solutions[j] == (math.floor(math.sqrt(N) - M + i + 1) % Base[j]) or (math.floor(math.sqrt(N) - M + i + 1) % Base[j]) == (Base[j] - Solutions[j]): 
                    
                                                                
                    zeroMatrix[i][j] = math.floor((0.5) + math.log(Base[j]))    #add .5 + logp
                i = i + 1     
            j = j + 1                                                           #do this for all rows and columns 
            
            
            
        #print("Printing filled zeroMatrix: ")                      #now we have zeroMatrix + .5 + logp
        #print(zeroMatrix)                                          #we can print it
        
        rowSum = []                                                 #create an array holder to hold sums on rows
        for x in range(2*M):                                        #of size 2*M to sum on all rows 
                rowSum.append(0)                                    #fill it all with zeros 
        
     
        i = 0                                                       #i counts the rows 
        while i < (2*M):                                            #for all the rows 
            j = 0                                                   #j counts the columns 
            while j < B-1:                                          #for all the columns 
                rowSum[i] = rowSum[i] + zeroMatrix[i][j]            #rowSum[i] sums across rows 
                j = j + 1
            i = i + 1                                               #need to do this for all rows and columns 
            
        #print("printing a row sum: ")                              #rowSum holds sum on all 2*M total rows 
        #print(rowSum)                                              #we can print it then 
        
        
        T = 1.5                                                     #we pick a threshold and calculate target
        atLeast = ((0.5)*(math.log(N)) + (math.log(M)) - (T)*(math.log(Base[B-2])))
        

        passes = []                                                 #passes holds indices of rows that >= target
                                                                    #hence they pass the test 
                                                                    
        i = 0                                                       #i here counts the rows, so we count all rows
        while i < (2*M):                                            #go over all rows 
            if rowSum[i] >= atLeast:                                #if we pass the test 
                passes.append(i)                                    #add it to our passes array
            i = i + 1                                               #now passes holds all row indices that pass                 
        #print("Here is what rows passed:")                         #we can print that array 
        #print(passes)                    

                                                                    #Start Trial Division...
                                                                    #Do this on each Qri that passes the test 
                                                                    #Q(ri) = abs((ri**2)-n) and ri = (math.floor(math.sqrt(N) - M + i))
        
        exponents = []                                              #holds exponent results trial division
        factors = []                                                #holds factor results trial division
        
        masterexp = []                                              #final exponent matrix 
        masterprimes = []                                           #final primes matrix
        masterindex = []                                            #final index matrix

        index = 0                                                   #index counts how far we are into the passes array 
        while index < len(passes):                                  #while we still have index's that passes the target test 
            
            Q = abs(((math.floor(math.sqrt(N) - M + passes[index] + 1))**2) - N)    #calculate Qri for each row 
            exponents, factors = trialDivision(Q,Q)                                 #get the results from trial division

            i = 0                                                   #i counts all of the factors 
            switch2 = 1                                             #
            while i < len(factors):                                 #while we still have factors
                
                j = 0                                               #j counts over primes in the base
                switch=0                                            #signals that the factor is in the factor Base
                
                while j < len(Base):                                #for all numbers in the factor Base
                    
                    if factors[i] == Base[j]:                       #if the factor is anywhere in the factor Base          
                        switch = 1                                  #flip switch to 1...the factor is in the factor Base
                    j = j + 1
                    
                if switch == 0:                                     #if we never found it 
                    switch2 = 0                                     #flip switch2 to low...
                i = i + 1                                           #do this for all factors in our factor array...
                
            if switch2 == 1:                                        #if we passed trialDiv, save the i, exponent, and prime arrays
            
                masterindex.append(index)
                masterprimes.append(factors)
                masterexp.append(exponents)
                
            index = index + 1                                       #...for all rows that passed the test 
                                                                    #now we have everything that passed
        #print("Here is masterindex")                                                      
        #print(masterindex)
        #print("Here is masterexp")                                 
        #print(masterexp)                                           #masterindex holds indices in passes array that completely factor over B
        #print("Here is masterprimes")                              #masterexp holds corresponding exponents 
        #print(masterprimes)                                        #masterprimes holds corresponding primes
        
        #Here we will print the table of factors and exponents:
        #masterexp and masterprimes have the same index and line up
        
        
        print("About to Print Factors")
        print("Note that the index in prime factor array corresponds to the same index of the exponent")
        i = 0 
        while i < len(masterindex):

            print(repr(passes[masterindex[i]]) + " =  prime factors: " + repr(masterprimes[i]) + " raised to exponents: " + repr(masterexp[i]))
                    
            i = i + 1

        print("Done Printing Factors")
       
        bigContainer= []                                            #bigContainer will hold all containers       

        t=0                                                         #t counts indices in masterindex
        while t < len(masterindex):                                 #while we still have elements in masterindex...complete factorizations
        
            container = []                                          #container is an array the size of the Base - 1
            for i in range(B-1):
                    container.append(0)
                    
            i=0                                                     #i counts indices in the factor base 
            while i < len(Base):                                    #so over all elements in the factor base...
            
                j=0                                                 #j counts indices of primes that completely factored 
                while j < len(masterprimes[t]):                     #so over all elements in the primes that completely factor...
                
                    if Base[i] == masterprimes[t][j]:                   
                        container[i] = masterexp[t][j]              #build the exponent matrix 

                    j = j + 1                                       #increment up the list of good primes
                    
                i = i + 1                                           #increment up the base 
                
            bigContainer.append(container)                          #append that whole row to bigContainer
            
            t = t + 1                                               #increment up the master index list 
            
        #print(bigContainer)
         
        
        i = 0                                                       #i counts over the rows of bigContainer                              
        while i < len(bigContainer):                                #while we're not at the end of the row
            bigContainer[i].insert(0,1)                             #append 1 at spot 0
            
            j=0                                                     #j counts over the columns 
            while j < len(bigContainer[0]):
                bigContainer[i][j] = bigContainer[i][j] % 2         #mod 2 every element 
                j=j+1
            i=i+1                                                   #over rows and columns 
            
        #create identity matrix 
        identity = [[1 if i == j else 0 for j in range(len(masterindex))] for i in range(len(masterindex))]
        #print(identity)
        
        i=0
        while i < len(bigContainer):
            bigContainer[i].extend(identity[i])                     #extend identity to each row 
            i = i + 1


        oneRows = []                                            #oneRows holds indexes of rows with a 1 where we want it
        j = B - 1                                               #j starts at the last column of the factor base 
        currentRow = 0                                          #currentRow holds the row we're manipulating at any iteration 
        
        while j > -1:                                           #while j is greater than 0... we haven't hit column 0 yet
            #print("j is " + repr(j) + ", row is " + repr(currentRow))
            
            i = currentRow                                      #currentRow is a counter for the row index
            while i < len(bigContainer):                        #while we haven't hit the bottom row...
                
                if bigContainer[i][j] == 1:                     #check to see if that spot is a 1...
                    oneRows.append(i)                           #if it is... save the index of that row to oneRows array 
                          
                i = i + 1                                       #do this check for all rows...good
                                                                #oneRows contains all indexes of lists with a desired 1                                      
                                                    
            i=1
            while i < len(oneRows):
                colnum=0
                while colnum < len(bigContainer[0]):
                    bigContainer[oneRows[i]][colnum]=  (bigContainer[oneRows[i]][colnum] +  bigContainer[oneRows[0]][colnum])%2
                    colnum = colnum + 1
                i = i + 1
            
    
                                                                            #now add current row to itself to eliminate it 
            z = 0                                                           #z is another counter for columns
            while (z < len(bigContainer[0])) and (len(oneRows)!=0):         #while we still have columns to go over 
                                                                            #add to itself 
                                                                            
                bigContainer[oneRows[0]][z] = (bigContainer[oneRows[0]][z] + bigContainer[oneRows[0]][z]) % 2
                
                z = z + 1
                                              
            oneRows = []                                    #delete all elements of oneRows array before re-entering
            #print(oneRows)

            #currentRow = currentRow + 1                    #go to the next row we want to reduce 
            j = j - 1                                       #move back a column 
                                                            #done
              
        #print("Printing Results of Row Reduction: ")       #can test the results of our row reduction
        #print(bigContainer)
        
                                                            #now its time to move onto Kraitchik's Test        
        i = 0
        while i < len(bigContainer):                        #while we still have values in bigContainer
        
            RIside=1                                        # ri side 
            PDside=1                                        # prime decomposition side
            
            j = B                                           #we're starting at spot at the end of the factor base
            
            while j < len(bigContainer[0]):                 #while still in that row
            
                if bigContainer[i][j] == 1:                 # get the corresponding i, and also grab his prime factor.
                    ri=(math.floor(math.sqrt(N)) - M +  passes[masterindex[j-B]]+1)
                    
                    RIside = (RIside * ri) % N              #accumulate RI 
                    l=0
                    
                    while l < len(masterexp[j-B]):          #while we still have exps
                       #print(passes[masterindex[j-B]])
                       
                        temp = masterexp[j-B][l]            #for the corresponding spots 
                        while temp > 0:
                            
                            PDside = int((PDside*(masterprimes[j-B][l]))%N) #accumulate PD
                            temp=temp-1
                        l=l+1
                j=j+1
                
            check = 0                                                                 #print the X's and the Y's 
            print("X=" + repr(RIside) + ", Y=" + repr(PDside))
            if (gcd((RIside-PDside),N) !=1 ) and (gcd((RIside-PDside),N) !=N):   #if passes, we have our number!!
                print("We found our factor!!!")
                check = 1
                
            i=i+1
        print("Done with Sieve.")
        if(check == 1):
            print("Success!!!")
        
#######################################################################

  

###################### Trial Division Function ########################
def trialDivision(n,m): # a positive integer n and a bound max
    i = 0
    f = n
    d = 2
    p = []
    e = []

    if f%d == 0:
        i = i + 1
        temp, f = maxPower(f,d)
        e.append(temp)
        p.append(d)
    d = 3
    while (d <= m) and ((d*d) <= f):
        if f % d == 0:
            i = i + 1
            p.append(d)
            temp, f = maxPower(f,d)
            e.append(temp)
        d = d + 2
    if f > 1 and (d*d) > f:
        i = i + 1
        p.append(f)
        e.append(1)
        f = 1
        
    return [e,p]
#######################################################################

      
        
######################### Tonelli Algorithm ##########################
def tonelli(a,p):
        
        b = 2;
        while jacobi(b,p) != -1:
                b = b + 1;
        s,t = maxPower(p-1,2)
        i = 2
        c = (a*(b*b))%p
        k=1
        while k <= (s-1):
                if fme(c,(2**(s-k-1))*(t),p) == (p-1):               #(c**(2**(s-k-1)*t) % p)...fme(c,2**(s-k-1)*t,p)
                        i = i + (2**k)                            
                        c = (c)*fme(b,(2**k),p)              #(c*(b**(2**k)) % p) ...fme(c,b**(2**k),p)
                k = k + 1;
        temp1 = fme(b,((i*t)/2),p)
        temp2 = fme(a,((t+1)/2),p)
        r = (temp1 * temp2) % p
        
                                                                  #temp1 = fme(b,((i*t)/2),p)
        #r = (b**((i*t)/2)*a**((t+1)/2))%p                        #temp2 = fme(a,(t+1)/2),p)

        if abs(p-r) < abs(r):                                  
                return (math.floor(p-r)) 
        else:
                return math.floor(r)       

########################################################################



######################### Jacobi Algorithm ############################                
def jacobi(a,m):
        a = a % m
        t = 1      
        while a != 0:
            c = 0              
            while a%2 == 0:
                a = a/2
                c = 1-c              
            if c == 1:
                if ((m % 8) == 3) or ((m % 8) == 5):
                    t = -1*t              
            if ((a%4) == 3) and ((m%4) == 3):
                t = -1*t                
            temp = m
            m = a
            a = temp 
            a = a % m
       
        if m == 1:
                return t
        return 0
#######################################################################                             


                
####################### Max Power of d function ########################             
def maxPower(n,d):
	e = 0
	f = n
	while (f % d) == 0:
		f = f/d
		e = e + 1
	return [e,f]       #n  = (d^e)(f)		
#######################################################################  		
		


###################### Get Factor Base Function #######################
def getFactorBase(N,M,B):
    
        Base = []                       #Base will hold the factor base 
        for i in range(B-1):
                Base.append(0)          #Equal to the size of the base -1           
                    
        primes = era(10000000)        
        
        counter = 0
        for x in primes:
                
            if jacobi(N, x) == 1:
                                
                Base[counter] = x
                counter = counter + 1;
                                
            if counter == B-1:
                break       
                
        return Base      
####################################################################### 
   

     
########################### GCD Function ##############################
def gcd(a,b):
    while b != 0:
        temp = b
        b = a % b
        a = temp
    return abs(a)
######################################################################



####################### Fast Modular Exponentiation ###################
def fme(b,e,m):
    n=1
    while e != 0:
        if e % 2 == 1:
            n = (n*b)%m
        e = math.floor(e/2)
        b = (b*b)%m

    return n
#######################################################################



################# Sieve of Eratosthenes ##############################
def era(n):
    i = 1
    l = []
    l.append(0)
    l.append(0)
    while i < n:
        l.append(1)
        i = i + 1
    
    p = 2
    while (p**2) <= n:
        j = p + p
        while j <= n:
            l[j] = 0
            j = j + p
        p = p + 1
        while l[p] == 0:
            p = p + 1
    
    h = []        
    h.append(2)
    j = 1
    p = 3
    while p < n:
        if l[p] == 1:
            h.append(p)
        j = j + l[p]
        
        p = p + 1
    return h
######################################################################



# my number 135291536006657
# bressoud's number 4999486012441

#calling the function first calls QSieve, which acts as main
QSieve(135291536006657,5000,1000)           
                



        
