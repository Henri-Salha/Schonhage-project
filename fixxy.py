# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 22:01:24 2023
Implémente Fixxy: nb entier sous forme m*pow(2,n) et Coffy sa version complexe
Calcule  les racines nièmes complexes de l'unité sous format Coffy
Contient un module d'export de tables de Coffy sous .csv'
@author: henri
"""

import numpy as np
import csv

class Fixxy ():
    ''' mantissa*pow(2,exp)'''
    def __init__(self,mantissa=0,precision=-36):
        self.mantissa = int(mantissa) #évite int64
        self.exp = precision
        
    @classmethod
    def fromvalue(cls, value=0, precision=-36):
        '''calculates mantissa from decimal value +requested precision'''
        m = int(value*pow(2,-precision))
        return cls(m,precision)
   
    def __add__(self,other):
        if self.exp != other.exp: return Fixxy(-999,0)
        return Fixxy(self.mantissa + other.mantissa,self.exp)

    def __sub__(self,other):
        if self.exp != other.exp: return Fixxy(-999,0)
        return Fixxy(self.mantissa - other.mantissa,self.exp)
     
    def __mul__(self,other):
        if self.exp != other.exp: return Fixxy(-999,0)
        (m1,m2) = (int(self.mantissa),int(other.mantissa))#évite int64
        m = Fixxy(m1*m2,2*self.exp)
        m3 = m.drop_precision(-self.exp)
        return m3
    
    def pow2(self,n):
        '''multiplies a Fixxy by pow(2,n)'''
        m = self.mantissa << n if n>=0 else self.mantissa >> (-n)
        return Fixxy(m,self.exp)
     
    def drop_precision(self,drop):
        ''' drop precision by drop factor (positive)'''
        m = self.mantissa
        s = np.sign(m)
        m1 = s*(abs(m) >> drop)
        e = self.exp + drop
        return Fixxy(m1,e)
    
    def more_precision(self,more):
        ''' increase precision by more factor (positive)'''
        m = self.mantissa
        m1 = m << more
        e = self.exp - more
        return Fixxy(m1,e)
    
    def toFloat(self):
        '''converts a fixxy to float'''
        return self.mantissa*pow(2,self.exp)

    def __eq__(self,other):
        return (self.mantissa == other.mantissa) & (self.exp == other.exp)
     
    def isqrt(self):
        ''' Fixxy square root'''
        # t = 2 if self.exp%2 else 1
        # m = self.mantissa * t
        m = self.mantissa << (-self.exp)
        x = isqrt_int(m)
        # x = x << (-self.exp//2)
        return Fixxy(x,self.exp)
    

def div (a,b):
    '''divides two Fixxies'''
    if (a.exp != b.exp) or (b.mantissa ==0): return Fixxy(-999,0)
    l1 = 0 #est-ce que j'ai raison de faire l'opération suivante?
    l1 = binsize(a.mantissa) - binsize(b.mantissa) 
    l2 = l1 +a.exp
    a1 = a.mantissa  << (-l2) if l2<0 else a.mantissa >> l2 
    q = (a1 // b.mantissa)
    if l1 >=0:
        q = q << l1
    else:
        q = q >> (-l1)
    return Fixxy(q, a.exp)

    
def isqrt_int(n):
    '''Newton's algorithm for square root'''
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

    
class Coffy ():
    '''complex with real and imag in Fixxy format'''
    '''real and complex must have same exponent'''
    def __init__(self,real,imag):
        if real.exp != imag.exp:
            self.real = self.imag = Fixxy(-999,0)
        else:
            self.real = real
            self.imag = imag
    
    @classmethod
    def fromvalue(cls, real=0, imag = 0, precision=-36):
        '''calculates Coffy from decimal value of complex and requested prcsiion'''
        return cls(Fixxy.fromvalue(real,precision),Fixxy.fromvalue(imag,precision))  
    
    def __add__(self,other):
        a = Coffy(self.real+other.real,self.imag+other.imag)
        return a

    def __sub__(self,other):
        a = Coffy(self.real-other.real,self.imag-other.imag)
        return a
    
    def __mul__(self,other):
        r = self.real * other.real - self.imag * other.imag
        i = self.real * other.imag + self.imag * other.real
        a =  Coffy(r,i)
        return a
    
    def multNum(self,num):
        ''' multipies a Coffy with a Fixxy '''
        a = Coffy(self.real*num,self.imag*num)
        return a
    
    def pow2(self,n):
        ''' multiplies a coffy with pow(2,n)'''
        return Coffy(self.real.pow2(n),self.imag.pow2(n))
    
    def drop_precision(self,drop):
        '''see fixxy drop_precision'''
        return Coffy(self.real.drop_precision(drop),self.imag.drop_precision(drop))
    
    def more_precision(self,more):
        '''see fixxy more-precision'''
        return Coffy(self.real.more_precision(more),self.imag.more_precision(more))
    
    def divNum(self,num):
        ''' divides a Coffy with Fixxy '''
        if num.mantissa == 0: return self
        a = Coffy(div(self.real,num),div(self.imag,num))
        return a
    
    def toComplex(self):
        ''' transforms Coffy in Complex number '''
        return complex(self.real.toFloat(),self.imag.toFloat()) 

        
    def conj(self):
        '''takes the conjugate of a Coffy (inverse when modulus=1)'''
        y = Fixxy(-self.imag.mantissa,self.imag.exp)
        a =  Coffy(self.real,y)
        return a
    
    def arg(self):
        ''' returns the arg of complex number (type Fixxy) '''
        sq_mod = self.real * self.real + self.imag * self.imag
        modulus = sq_mod.isqrt()
        a = self.divNum(modulus)
        return a #type Coffy

def power_roots (n,precision):
    '''computes Coffy array of size 2^n: exp(2*pi*i*k/2^n) '''
    #add_prec = 0 #précision additionnelle
    oo = Coffy.fromvalue(1,0,precision)#+add_prec)
    ur = unit_roots(n,precision)#+add_prec)
    pr = [[ur[0]]]
    for k in range (1,n+1):
        prk = [ur[0]]
        for l in range (1,pow(2,k)):
            s = ur[k] if (l % 2) else oo
            #print(k,l,", s = ", s.toComplex(),", fpr = ",pr[k-1][l//2].toComplex())
            prk.append(pr[k-1][l//2]*s)
        pr.append(prk)
    #pr1 = [x.drop_precision(-add_prec) for x in pr[n]]
    return pr[n]
    
def unit_roots (n,precision):
    '''computes Coffy array of size n: exp(2*pi*i/2^k) for k in range n '''
    oo = Coffy.fromvalue(1,0,precision)
    mo = Coffy.fromvalue(-1,0,precision)
    io = Coffy.fromvalue(0,1,precision)
    ur = [oo,mo,io] 
    if n == 2: return ur
    for i in range (3,n+1):
        w = ur[i-1] + oo
        ur.append(w.arg())
    return ur

def binsize (n):
    'nb of bits of an integer'
    if n == 0: return 0
    return 1+binsize(n//2)


def export (a,name): 
    ''' exports an array of Coffy in CSV file with name'''
    filename = name+".csv"
    mantissas = [[x.real.mantissa,x.imag.mantissa] for x in a]
    array = [["Precision:",-a[0].real.exp]]+mantissas
    # opening the file
    with open(filename, "w", newline="") as f:
        # creating the writer
        writer = csv.writer(f)
        # using writerows, all rows at once
        writer.writerows(array)

def export_series (a,name): 
    ''' exports an array of array of Coffy in CSV file with name'''
    filename = name+".csv"
    mantissas = list()
    base = len(a[0])
    print(f"Export Base:{base}")
    for i in range(base):
        mantissas.append(list())
        for j in range (len(a)):
            re = a[j][i].real.mantissa
            im = a[j][i].imag.mantissa
            b = 0#max(binsize(re),binsize(im))
            mantissas[i] += [re,im,b]
    num = list() #numérotation des colonnes
    mult = list() #le w[i] multiplicateur
    for i in range(base):
        num += [i," "," "] 
        mult += [a[1][i].real.mantissa,a[0][i].imag.mantissa," "]
    header = [num,mantissas[1],["-------"]*base]
    array = [["Precision:",-a[0][0].real.exp]]+header+mantissas
    # opening the file
    with open(filename, "w", newline="") as f:
        # creating the writer
        writer = csv.writer(f)
        # using writerows, all rows at once
        writer.writerows(array)


# n = 6
# base = pow(2,n)
# u = power_roots(n,-36)
# v = [wx.conj() for wx in power_roots(n,-36)]
# s= [[u[0]*u[(i*k)%base] for i in range(base)] for k in range(base)]
# export(v,'conj-power6multpres36')

               