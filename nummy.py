# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 10:35:59 2023

Implémente les nb entiers et entiers complexes sous forme
Somme (m*pow(2,exp)) où exp est variable
(la multiplication de deux nb donne m1*m2*power(2,exp1+exp2))
vs Fixxy qui garde exp constant
@author: henri
"""

import numpy as np

class Nummy ():
    def __init__(self,mantissa=0,exp=0,neg=False):
        self.mantissa = abs(mantissa)  #important: mantissa is unsigned int
        self.exp = exp #maybe negative
        if mantissa < 0: 
            self.neg = not(neg)
        else: 
            self.neg = neg
    
    def __add__(self,other):
        l = self.exp - other.exp
        m1 = self.mantissa
        m2 = other.mantissa
        e = self.exp
        if l > 0:
            m1 = m1 << l
            e = other.exp
        if l < 0:
            m2 = m2 << (-l)
        if self.neg == other.neg : return Nummy(m1+m2,e, self.neg)
        t = self.neg if m1 > m2 else other.neg
        return Nummy(abs(m1-m2),e,t)

    def inv_neg(self):
        'changes sign of Nummy'
        return Nummy(self.mantissa,self.exp,not(self.neg))        

    def __sub__(self,other):
        return (self + other.inv_neg())
    
    def toInt(self):
        'converts Nummy to Int'
        if self.exp <0: return 0
        m = self.mantissa << self.exp
        if self.neg : m = -m
        return m
    
    def toFloat(self):
        'converts Nummy to Float'
        return self.mantissa*pow(2,self.exp)*pow(-1,self.neg)
    
    def reduce(self):
        ' simplifies the mantissa by factors of 2'
        m = self.mantissa
        e = self.exp
        while not(m % 2) and m>0:
            m = m  // 2
            e +=1
        return Nummy(m,e,self.neg)
    
    def expand(self,precision):
        'increases or decreases the mantissa to reach precision'
        l = precision - binsize(self.mantissa)
        if  l >= 0: 
            m = self.mantissa << l # ajoute de la précision
        else:
            m = self.mantissa >> (-l) #enlève de la précision
        e = self.exp - l
        return Nummy(m,e,self.neg)
    
    def __eq__(self,other):
        return self.toInt() == other.toInt()
    
    def __mul__(self,other):
        a = self.reduce()
        b = other.reduce()
        m = a.mantissa*b.mantissa
        e = a.exp+b.exp
        s = a.neg^b.neg
        return Nummy(m,e,s)
    
    def isqrt(self,precision):
        # preparation of number for Newton's algorithm
        if self.neg : return Nummy()
        a = self.expand(2*precision)
        e = a.exp
        m = a.mantissa
        if (e % 2): #make sure exp is pair
            m = m << 1
            e -= 1 
        # Newton's algorithm for square root
        x = m 
        y = (x + 1) // 2
        while y < x:
            x = y
            y = (x + m // x) // 2
        return Nummy(x,e//2)
    

def div (a,b,precision):
    'division de Nummies avec précision'
    b1 = b.reduce()
    bn = binsize(b.mantissa)
    l = bn + precision  #
    a1 = a.expand(l)
    m = a1.mantissa // b1.mantissa
    e = a1.exp - b1.exp
    s = a1.neg ^ b1.neg
    return Nummy(m,e,s)

    
class Cummy ():
    def __init__(self,real=Nummy(0),imag=Nummy(0)):
        self.real = real
        self.imag = imag
        self.ghost = complex(real.toFloat(),imag.toFloat())
    
    def __add__(self,other):
        a = Cummy(self.real+other.real,self.imag+other.imag)
        a.ghost = self.ghost + other.ghost
        return a

    def __sub__(self,other):
        a = Cummy(self.real-other.real,self.imag-other.imag)
        a.ghost = self.ghost - other.ghost
        return a
    
    def __mul__(self,other):
        r = self.real * other.real - self.imag * other.imag
        i = self.real * other.imag + self.imag * other.real
        a =  Cummy(r,i)
        a.ghost = self.ghost * other.ghost
        return a
    
    def multNum(self,num):
        ''' mult with Nummy '''
        a = Cummy(self.real*num,self.imag*num)
        a.ghost = self.ghost * num.toFloat()
        return a
    
    def divNum(self,num,precision):
        ''' mult with Nummy '''
        if num.mantissa == 0: return self
        a = Cummy(div(self.real,num,precision),div(self.imag,num,precision))
        a.ghost = self.ghost / num.toFloat()
        return a
    
    def expand(self,precision):
        r = self.real.expand(precision)
        i = self.imag.expand(precision)
        a = Cummy(r,i)
        a.ghost = self.ghost
        return a
    
    def toComplex(self):
        ''' transforms Cummy in Complex number '''
        return complex(self.real.toFloat(),self.imag.toFloat()) 
    
    def checkError(self):
        return self.toComplex() - self.ghost
        
    def conj(self):
        a =  Cummy(self.real,self.imag.inv_neg())
        a.ghost = np.conj(self.ghost)
        return a
    
    def arg(self,precision):
        ''' returns the arg of complex number (type Nummy) '''
        sq_mod = self.real * self.real + self.imag * self.imag
        modulus = sq_mod.isqrt(precision)
        a = self.divNum(modulus,precision)
        a.ghost = self.ghost/np.abs(self.ghost)
        return a #type Cummy

def power_roots (n,precision):
    '''computes exp(2*pi*i*k/2^n) '''
    ur = unit_roots(n,precision)
    pr = [[ur[0]]]
    for k in range (1,n+1):
        prk = [ur[0]]
        for l in range (1,pow(2,k)):
            s = ur[k] if (l % 2) else Cummy(Nummy(1),Nummy(0))
            #print(k,l,", s = ", s.toComplex(),", fpr = ",pr[k-1][l//2].toComplex())
            prk.append(pr[k-1][l//2]*s)
        pr.append(prk)
    return pr[n]
    
def unit_roots (n,precision):
    '''computes all exp(2*pi*i/2^k) for k in range n '''
    ur = [Cummy(Nummy(1),Nummy(0)),Cummy(Nummy(-1),Nummy(0)),Cummy(Nummy(0),Nummy(1))] 
    if n == 2: return ur
    for i in range (3,n+1):
        w = ur[i-1] + Cummy(Nummy(1),Nummy(0))
        ur.append(w.arg(precision))
    return ur


def binsize (n):
    'nb de bits d un entier'
    if n == 0: return 0
    return 1+binsize(n//2)