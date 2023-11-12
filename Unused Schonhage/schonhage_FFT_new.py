# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:13:41 2023

@author: henri
"""

import nummy as nm
import numpy as np

def diff_mult (a,b,precision=36,ghost=0):
    print ("Python mult: ",a*b)
    print ("Fourier mult: ", mult_fft(a, b,precision))
    return a*b-mult_fft(a,b,precision)[ghost]

def mult_fft (a,b,precision=36):
    inputsize = binsize(max(a,b)) # schonhage p505
    n = 0
    while n*pow(2,n)<2*inputsize:
        n +=1
    base = pow(2,n)
    invsq_base = nm.Nummy(1,-2*n,False) # = 1/2^(2n)
    base_4n = nm.Nummy(1,4*n,False) # = 2^(4n)
    print ("n:", n, " base:",base)#
    b1= [x * invsq_base for x in decomp(b,n)]
    a1= [x * invsq_base for x in decomp(a,n)] #decomp in powers of 2^n and divides by 2^(2n)
    ac = [nm.Cummy(w,nm.Nummy()) for w in a1] #rend complexe le vecteur réel
    bc = [nm.Cummy(w,nm.Nummy()) for w in b1] #rend complexe le vecteur réel
    a2 = myfft(ac,n,precision) #précision = 6n, source: Schonhage 
    b2 = myfft(bc,n,precision) 
    c2 = [x*y for x,y in zip(a2,b2)]
    cc = myifft (c2,n,precision) # Cummy
    c1 = [x.expand(precision) for x in cc]
    c = comp (c1,n).multNum(base_4n) # Cummy
    store = [ac,bc,a2,b2,c2,c1,c,np.round(c.toComplex().real,0)]
    return store #np.round([c.real.toFloat(),c.ghost.real],0)

def binsize (n):
    'nb de bits d un entier'
    if n == 0: return 0
    return 1+binsize(n//2)

def decomp (a,n):
    ''' decomposes a in factors of 2^n.i '''
    base = pow(2,n)
    al = list()
    while a > 0:
        al.append(nm.Nummy(a % base))
        a = a // base
    al = list_complete (al,base,nm.Nummy(0))
    return al

def comp (a,n): #à faire
    x = nm.Cummy(nm.Nummy(),nm.Nummy())
    for i in range(pow(2,n)):
        ii = nm.Nummy(1,n*i,False)
        y = a[i].multNum(ii)
        z = a[i].real
        print (i,"a[i]:",z.mantissa*pow(-1,z.neg),z.exp,"2^ni=",\
               ii.toInt(),"result=",np.round(y.toComplex().real,10))
        x = x + y
    return x

def list_complete (a,n,x):
    ' completes a list a until length n with object x'
    b = n - len(a)
    while b> 0:
        a.append(x)
        b -= 1 
    return a


def myfft (a, n, precision):
    'tf de Fourier discrète'
    base = pow(2,n)
    w = nm.power_roots(n,precision)
    a1 = list()
    for i in range(base):
        a1.append(nm.Cummy(nm.Nummy(),nm.Nummy())) # 0
        for k in range(base):
            k1 = (i*k) % base # prend le modulo 
            a1[i] = a1[i] + a[k]*w[k1]
    return a1

def myifft (a, n, precision):
    'tf de Fourier discrète inverse'
    base = pow(2,n)
    inv_base = nm.Nummy(1,-n,False) # = 1/2^n en Nummy
    w = [wx.conj() for wx in nm.power_roots(n,precision)]
    a1 = list()
    for i in range(base):
        a1.append(nm.Cummy(nm.Nummy(),nm.Nummy())) # 0
        for k in range(base):
            k1 = (i*k) % base # prend le modulo 
            a1[i] = a1[i] + (a[k]*w[k1]).multNum(inv_base)#div par 2^n
    return a1

def schonhage_scale (n):
    ''' displays the key numbers in schonhage's scales'''
    b = n//3
    bigB = pow(2,b)
    bigN = n*pow(2,n-1)
    maxNum = pow(2,bigN)
    print ("b = ",b)
    print ("B-scale =",bigB)
    print ("n =", n )
    print ("Max bitsize = ", bigN)
    print ("Max number = ", maxNum)


t1 = 3543
t2 = 5421

a = mult_fft(t1,t2,36)



