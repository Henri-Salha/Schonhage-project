# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:13:41 2023

@author: henri
"""

import numpy as np

def test_mult_c():
    for i in range(0,40):
        x = 0
        j = 0
        while abs(x) < 1 and j<41:
            j+=1
            x = diff_mult_c(pow(2,i)-1,pow(2,j)-1)
        print (i,j,"diff = ",x)


def diff_mult_c (a,b):
    # print ("Python mult: ",a*b)
    # print ("Fourier mult: ", mult_fft(a, b))
    return np.longdouble(a*b)-mult_fft_c(a,b)[7]

def mult_fft_c (a,b):
    inputsize = binsize(max(a,b)) # schonhage p505
    n = 0
    while n*pow(2,n)<2*inputsize:
        n +=1
    base = pow(2,n)
    #print ("Base:",base)
    a1= decomp_c(a,base)/(base*base)
    b1= decomp_c(b,base)/(base*base)
    a2 = myfft_c(a1,base) # (np.fft.fft(a1,base))
    b2 = myfft_c(b1,base) # (np.fft.fft(b1,base))
    c1 = c2 = np.array([0]*base,dtype=np.clongdouble)
    for i in range(base):
        c2[i] = a2[i]*b2[i]
    c1 = myifft_c (c2, base) # np.fft.ifft(c2,base) 
    c = comp_c (c1,base) * np.clongdouble(pow(base,4))
    store = [a1,b1,a2,b2,c2,c1,c,np.round(np.real(c),0)]
    return store # round(np.real(c),0)

def binsize (n):
    'nb de bits d un entier'
    if n == 0: return 0
    return 1+binsize(n//2)

def decomp_c (n,base): 
    a = np.zeros(base,dtype=np.clongdouble)
    i = 0
    while n > 0:
        a[i] = n % base
        n = n // base
        i += 1
    return a
    
def comp_c (arr,base):
    n = np.clongdouble(0)
    for i in range(base):
        y = arr[i]*np.clongdouble(pow(base,i))
        #print (i,np.round([arr[i],pow(base,i),y],10))
        n += y
    return n

def myfft_c (a, base):
    a1 = np.array([0]*base,dtype=np.clongdouble)
    n = int(np.log2(base))
    w = power_roots_c(n)
    for i in range(base):
        for k in range(base):
            k1 = (i*k) % base # prend le modulo 
            #a1[i] += a[k]*np.power(w,i*k)
            a1[i] += a[k]*w[k1]
    return a1

def myifft_c (a, base):
    a1 = np.array([0]*base,dtype=np.clongdouble)
    n = int(np.log2(base))
    w = np.conj(power_roots_c(n)) #inverse = conjugué
    for i in range(base):
        for k in range(base):
            k1 = (i*k) % base # prend le modulo 
            #a1[i] += a[k]*np.power(w,i*k)
            a1[i] += a[k]*w[k1]/base
    return a1

def power_roots_c (n):
    '''computes exp(2*pi*i*k/2^n) with python complex'''
    ur = unit_roots_c(n)
    pr = [[ur[0]]]
    for k in range (1,n+1):
        prk = [ur[0]]
        for l in range (1,pow(2,k)):
            s = ur[k] if (l % 2) else 1
            prk.append(pr[k-1][l//2]*s)
        pr.append(prk)
    return pr[n]

def unit_roots_c (n):
    '''computes all exp(2*pi*i/2^k) for k in range n with python complex '''
    ur = [complex(1,0),complex(-1,0),complex(0,1)] 
    if n == 2: return ur
    for i in range (3,n+1):
        w = ur[i-1] + complex(1,0)
        d = np.abs(w)
        ur.append(complex(w.real/d,w.imag/d))
    return ur

a = mult_fft_c(3543,5421)
