# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:13:41 2023

J'ai des pb de rounding que je ne devrai pas avoir, yc. sur 
l'algorithme complexe. Je dois essayer de faire le rounding là-dessus
pour voir si ça marche.
J'ai un pb d'arrondi aux très basses valeurs, mais qui s'accumule

@author: henri
"""

import fixxy as fx
import numpy as np


def mult_fft (a,b):
    inputsize = binsize(max(a,b)) # schonhage p505
    n = 0
    while n*pow(2,n)<2*inputsize:
        n +=3 #n+=3 pour Schonhage
    base = pow(2,n)
    precision = -6*n # papier de Schonhage: -6*n
    print ("n:", n, " base:",base)#
    b1= [x.pow2(-2*n) for x in decomp(b,n,precision)] #array of Fixxy
    a1= [x.pow2(-2*n) for x in decomp(a,n,precision)] #decomp in powers of 2^n and divides by 2^(2n)
    ac = [fx.Coffy(w,fx.Fixxy(0,precision)) for w in a1] #array of Coffy
    bc = [fx.Coffy(w,fx.Fixxy(0,precision)) for w in b1] #(translates to complex)
    a2 = myfft(ac,n)# array of Coffy
    b2 = myfft(bc,n)  # array of Coffy
    c2 = [x*y for x,y in zip(a2,b2)] # array of Coffy
    c1 = myifft (c2,n) # array of Coffy
    m = extract(c1) # Coffy
    result = sum([m[i]*pow(2,n*i) for i in range(pow(2,n))])
    #store = [ac,bc,a2,b2,c2,c1,c,np.round(c.toComplex().real,0)]
    print("Comparaison:",a*b,result)
    return result#store #np.round([c.real.toFloat(),c.ghost.real],0)

def binsize (n):
    'nb de bits d un entier'
    if n == 0: return 0
    return 1+binsize(n//2)

def decomp (a,n,precision):
    ''' decomposes a in factors of 2^n.i '''
    base = pow(2,n)
    al = list()
    while a > 0:
        al.append(fx.Fixxy.fromvalue(a % base,precision))
        a = a // base
    al = list_complete (al,base,fx.Fixxy(0,precision))
    return al

def list_complete (a,n,x):
    ' completes a list a until length n with object x'
    b = n - len(a)
    while b> 0:
        a.append(x)
        b -= 1 
    return a

def extract (a):
    '''extracts from an array of Coffy the multiples in base 2^n'''
    precision = -a[0].real.exp
    n = binsize(len(a)-1)
    overflow = pow(2,n-1)
    m = [x.real.mantissa+overflow for x in a]#pour les arrondis négatifs
    m1 = [x >> (precision - 4*n) for x in m]
    return m1

def myfft (a, n):
    'tf de Fourier discrète'
    precision = a[0].real.exp
    base = pow(2,n)
    w = fx.power_roots(n,precision)
    a1 = list()
    for i in range(base):
        a1.append(fx.Coffy.fromvalue(0,0,precision))
        for k in range(base):
            k1 = (i*k) % base # prend le modulo 
            a1[i] = a1[i] + a[k]*w[k1]
    return a1

def myifft (a, n):
    'tf de Fourier discrète inverse'
    precision = a[0].real.exp
    base = pow(2,n)
    w = [wx.conj() for wx in fx.power_roots(n,precision)]
    a1 = list()
    for i in range(base):
        a1.append(fx.Coffy.fromvalue(0,0,precision))
        for k in range(base):
            k1 = (i*k) % base # prend le modulo 
            a1[i] = a1[i] + (a[k]*w[k1]) #div par 2^n
        a1[i] = a1[i].pow2(-n)
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


t1 = 549195616#pow(2,192)-1#4294967295#266305#3543
t2 = 5421

n= 6
precision = -6*n


b0 = fx.Coffy.fromvalue(0,0,precision)
#prec = fx.Coffy(fx.Fixxy(6,precision),fx.Fixxy(6,precision))



t1b = [w.pow2(-2*n) for w in decomp(t1, n, precision)]
t1c = [fx.Coffy(w,fx.Fixxy(0,precision)) for w in t1b]
t1f = myfft(t1c, n)  
t1m = [x*x for x in t1f]
t1i = [w for w in myifft(t1m, n)]
#c = [comp(t1i,n,precision).pow2(-6*n-n+4*n)]+[b0]*(pow(2,n)-1)#63
print(len(t1c),len(t1f),len(t1i))#,len(c))
#t1p = [w + prec for w in t1i]
#print (t1*t2, c[0].real.toFloat())#,c[0].real.mantissa)
m = extract(t1i)
result = sum([m[i]*pow(2,n*i) for i in range(pow(2,n))])
print(result,t1*t1)
c = [fx.Coffy.fromvalue(x,0,0) for x in m]
#fx.export_series([t1c,t1f,t1i,c], "analysis")



