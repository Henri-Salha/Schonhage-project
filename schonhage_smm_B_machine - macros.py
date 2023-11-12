# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 22:37:17 2023
Schonhage SMM machines (Storage Modification Machines)
Based on Schonhage's 1980 paper
@author: Henri Stephanou
this file defines macros running on the B-scale SMM machine
used for the multiplication algorithm
@author: henri
"""

import schonhage_smm_B_machine as smmB

def label (tag): return (lambda x: tag+f'{x}')

def macro_bin_input(var,id_mac="0"):
    #converts input of b bits into B-scale and puts it in "var"
    #using register "acc"
    varb = "#bi"#compteur quelconque
    lbl = label("MBI"+id_mac)
    prg = [(0,"decl",varb),
        (0,"set",varb,var+"S"),
           (lbl(1),"input",lbl(3),lbl(2)),
           (0,"goto",lbl(6),0),
           (lbl(2),"set",varb+"P",varb),#value = 1
           (0,"goto",lbl(4),0),
           (lbl(3),"set",varb+"P",var),#value = 0
           (lbl(4),"set",varb,varb+"S"),
           (0,"goto",lbl(1),0),
           (lbl(6),"test",varb,var),
           (0,"goto",lbl(7),0),
           (0,"set",varb+"P",var), #value = 0
           (0,"set",varb,varb+"S"),
           (0,"goto",lbl(6),0),
           (lbl(7),"pass",0,0)]
    prg += macro_bin_to_B(var,id_mac)
    return prg
          
def macro_bin_to_B(var,id_mac="0"):
    #converts input of b bits into B-scale and puts it in "var"
    #using register "acc"
    # on 4-bits: B= b0+2^(b1+2^(b2+2^b3))
    # starts with b3
    varb = "#bE1"
    def bin_to_B_unit(unit):
        #unit = P (units) or Q (tens)
        varB = var+unit
        lbl = label("MbtB"+id_mac+unit)
        unit_prg = [(0,"set",varb,var+"S"),
               (0,"set",varB,"W"),
               (lbl(1),"test",varb+unit,var), #teste bit=0?
               (0,"goto",lbl(2),0),
               (0,"set",varB,varB+"S"),
               (lbl(2),"set",varb,varb+"S"),
               (0,"test",varb,var),
               (0,"goto",lbl(6),0),
               (0,"set",varB,varB+"P"),#met à la puissance 2
               (0,"goto",lbl(1),0),
               (lbl(6),"pass",0,0)]
        return unit_prg
    prg = [(0,"decl",varb)]+ bin_to_B_unit('P')+bin_to_B_unit('Q')
    return prg

def macro_B_to_bin(var,id_mac="0"):
    #program to check -- seems odd
    varb = "#Bb1"
    varB = "#Bb2"
    def B_to_bin(unit):
        lbl = label("MbtB"+id_mac+unit)
        unit_prg = [(0,"set",varb,var+"W"),#goto Vb0
               (0,"set",varB,var+unit),
               (lbl(0),"set",varb+unit,var),#init à 0 on units
               (0,"set",varb,varb+"W"),
               (0,"test",varb,var), #teste si a fini
               (0,"goto",lbl(1),0),
               (0,"goto",lbl(0),0),
               (lbl(1),"set",varb,varb+"W"),
               (0,"test",varB+"QP",varB), #test if even
               (0,"goto",lbl(3),0),
               (0,"set",varb+unit,varb),#met le bit à 1
               (lbl(3),"set",varB,varB+"Q"),
               (0,"test",varB,""),
               (0,"goto",lbl(7),0),
               (0,"test",varb+"W",var),
               (0,"goto",lbl(7),0),
               (0,"goto",lbl(1),0),
               (lbl(7),"pass",0,0)]
        return unit_prg
    prg = [(0,"decl",varb,varB)]+ B_to_bin("P")+B_to_bin("Q")
    return prg

def macro_bit_shift(var,id_mac="0",B_convert=True):
    varb = "#BS1"
    lbl = label("Mbsh"+id_mac)
    prg = [(0,"decl",varb),
           (0,"set",varb,var+"S"), #goto Vbn (largest power)-shift tens
           (lbl(1),"test",varb+"S",var), # test if finished
           (0,"goto",lbl(2),0),
           (0,"set",varb+"Q",varb+"SQ"), #shift bit
           (0,"set",varb,varb+"S"),
           (0,"goto",lbl(1),0),
           (lbl(2),"set",varb+"Q",var+"SP"),
           (0,"set",varb,var+"S"), #goto Vbn (larget power) -- shift unit
           (lbl(3),"test",varb+"S",var), # test if finished
           (0,"goto",lbl(4),0),
           (0,"set",varb+"P",varb+"SP"), #shift bit
           (0,"set",varb,varb+"S"),
           (0,"goto",lbl(3),0),
           (lbl(4),"set",varb+"P",var)] #smallest bit=0
    if B_convert:
        prg += macro_bin_to_B(var,"s"+id_mac)
    return prg

def macro_zero(var,id_mac="0"):
    #sets var to 0
    prg = [(0,"set",var+"P","W"),
           (0,"set",var+"Q","W")]
    prg += macro_B_to_bin(var,"zr"+id_mac)
    return prg

def macro_copy(var1,var2,id_mac="0"):
    #copies var1 into var2
    prg = [(0,"set",var2+"P",var1+"P"),
           (0,"set",var2+"Q",var1+"Q")]
    prg += macro_B_to_bin(var2,"cp"+id_mac)
    return prg

def macro_add(var1,var2,result,id_mac="0",B_convert=True):
    #adds two vars of two binary digits, first digit in 'P', second in 'Q' pointer
    #B_convert is an option to convert back to B_scale. Turned off for multiplication
    varb1 = "#A1"#"ZP"
    varb2 = "#A2"#"ZQ"
    varbr = "#A3"#"ZW"
    carry = "#A4"#"ZS"
    def add_unit(unit):
        lbl = label("Madd"+id_mac+unit)
        unit_prg = [(0,"set",varb1,var1+"W"),
               (0,"set",varb2,var2+"W"),#varb pointe vers le b0
               (0,"set",varbr,result+"W"),
               (lbl(1),"test",varb1,var1),#teste si la boucle de b est finie
               (0,"goto",lbl(10),0),
               (0,"test",varb1+unit,var1),#teste si b1=0
               (0,"goto",lbl(2),0),
               (0,"test",varb2+unit,var2),#b1=1teste si b2=0
               (0,"goto",lbl(3),0),
               (0,"test",carry,"W"), #b1=b2=1,teste si le carry est à 0
               (0,"goto",lbl(4),0), 
               (0,"set",varbr+unit,varbr), # cas 1-1-1: 0
               (0,"goto",lbl(9),0),
               (lbl(2),"test",varb2+unit,var2),#b1=0,teste si b2=0
               (0,"goto",lbl(6),0),
               (0,"test",carry,"W"), #b1=0,b2=1,teste si le carry est à 0
               (0,"goto",lbl(5),0),
               (lbl(4),"set",varbr+unit,result), #cas 0,1,1
               (0,"set",carry,"WS"),
               (0,"goto",lbl(9),0),
               (lbl(3),"test",carry,"W"),#b1=1,b2=0, teste si carry=0
               (0,"goto",lbl(5),0),
               (0,"goto",lbl(4),0),
               (lbl(5),"set",varbr+unit,varbr), #cas 1,0,0
               (0,"set",carry,"W"),
               (0,"goto",lbl(9),0),
               (lbl(6),"test",carry,"W"),#b1=0,b2=0, teste si carry=0
               (0,"goto",lbl(7),0),
               (0,"goto",lbl(5),0),
               (lbl(7),"set",varbr+unit,result), #cas 0,0,0
               (lbl(9),"set",varb1,varb1+"W"),
               (0,"set",varb2,varb2+"W"),
               (0,"set",varbr,varbr+"W"),
               (0,"goto",lbl(1),0),
               (lbl(10),"pass",0,0)]
        return unit_prg
    prg = [(0,"decl",varb1,varb2,varbr,carry),
           (0,"set",carry,"W")]+\
            add_unit('P')+\
            add_unit('Q')
    if B_convert:
            prg +=macro_bin_to_B(result,"a"+id_mac)
    return prg

def macro_substr(var1,var2,result,id_mac="0"):
    varb1 = "#S1"
    varb2 = "#S2"
    varbr = "#S3"
    carry = "#S4"
    def substr_unit(unit):
        lbl = label("Madd"+id_mac+unit)
        unit_prg = [(0,"set",varb1,var1+"W"),
               (0,"set",varb2,var2+"W"),#varb pointe vers le b0
               (0,"set",varbr,result+"W"),
               (lbl(1),"test",varb1,var1),#teste si la boucle de b est finie
               (0,"goto",lbl(10),0),
               (0,"test",varb1+unit,var1),#teste si b1=0
               (0,"goto",lbl(2),0),
               (0,"test",varb2+unit,var2),#b1=1teste si b2=0
               (0,"goto",lbl(3),0),
               (0,"test",carry,"W"), #b1=b2=1,teste si le carry est à 0
               (0,"goto",lbl(4),0), 
               (0,"set",varbr+unit,varbr), # cas 1-1-1
               (0,"goto",lbl(9),0),
               (lbl(3),"test",carry,"W"),#b1=1,b2=0, teste si carry=0
               (0,"goto",lbl(5),0),
               (lbl(4),"set",varbr+unit,result), #cas 1,0,1 ou 1,1,0
               (0,"set",carry,"W"),
               (0,"goto",lbl(9),0),
               (lbl(5),"set",varbr+unit,varbr), #cas 1,0,0
               (0,"goto",lbl(9),0),
               (lbl(2),"test",varb2+unit,var2),#b1=0,teste si b2=0
               (0,"goto",lbl(6),0),
               (0,"test",carry,"W"), #b1=0,b2=1,teste si le carry est à 0
               (0,"goto",lbl(7),0),
               (0,"set",varbr+unit,result), # cas 0-1-1
               (0,"goto",lbl(9),0),
               (lbl(6),"test",carry,"W"),#b1=0,b2=0, teste si carry=0
               (0,"goto",lbl(8),0),
               (lbl(7),"set",varbr+unit,varbr), # cas, 0,0,1 ou 0,1,0
               (0,"set",carry,"WS"),
               (0,"goto",lbl(9),0),
               (lbl(8),"set",varbr+unit,result), #cas 0,0,0
               (lbl(9),"set",varb1,varb1+"W"),
               (0,"set",varb2,varb2+"W"),
               (0,"set",varbr,varbr+"W"),
               (0,"goto",lbl(1),0),
               (lbl(10),"pass",0,0)]
        return unit_prg
    prg = [(0,"decl",varb1,varb2,varbr,carry),
           (0,"set",carry,"W")]+\
            substr_unit('P')+\
            substr_unit('Q')+\
            macro_bin_to_B(result,"u"+id_mac)
    return prg

def macro_mult(var1,var2,result,id_mac="0"):
    varb1="#M1"
    var3="#REG" #hidden register
    lbl=label("Mmx"+id_mac)
    prg = [(0,"decl",varb1)]+\
        macro_copy(var2, var3,"mx"+id_mac)+\
        [(0,"goto",lbl(0),0),#after copy, goto start of program
         (lbl("add"),"pass",0,0)]+\
        macro_add(var3, result, result,"mx"+id_mac,B_convert=False)+\
        [(0,"goto",lbl(2),0),
         (lbl("shf"),"pass",0,0)]+\
        macro_bit_shift(var3,"mx"+id_mac,B_convert=False)+\
        [(0,"goto",lbl(3),0),
         (lbl(0),"set",varb1,var1+"W"),#program starts here
         (lbl(1),"test",varb1,var1),#tests if complete turn
         (0,"goto",lbl(4),0),
         (0,"test",varb1+"P",varb1), #tests if bit = 1
         (0,"goto",lbl("add"),0), #if yes adds shifted var2 to the accumulator
         (lbl(2),"goto",lbl("shf"),0), #shifts var3 (=var2)
         (lbl(3),"set",varb1,varb1+"W"),
         (0,"goto",lbl(1),0),
         (lbl(4),"pass",0,0)]
    prg += macro_bin_to_B(var[2],id_mac="mx"+id_mac)
    return prg


p = smmB.SMM_Bscale(b=4,var=3)
var=p.vars
#pr0 = (macro_bin_input(var[0],"0"))
p.execute(macro_bin_input(var[0],"0"),inpt="1111")
p.execute(macro_bin_input(var[1],"1"),inpt="1001")
print(p.show_vars())
print ("After input:",p.var_values())
print ("Free pointers:", p.free_pointers)
print ("Used pointers:", p.used_pointers)

prg1 = (macro_mult(var[0],var[1],var[2]))
p.execute(prg1,print_exec=True,limit=10000)
print ("After mult:",p.show_vars(), p.var_values())



#prg = macro_add(var[0],var[1],var[2])
# p.execute(prg)
# print ("After addition",p.var_values())
# p.execute(macro_zero(var[2]))
# print ("After reset:",p.var_values())
#p.draw(1)
# prg2 = (macro_substr(var[0],var[1],var[2]))
# p.execute(prg2,print_exec=True,limit=10000)
# print ("After subst:",p.show_vars(), p.var_values())
# print("Copy program")
# p.execute(macro_copy(var[1], "#REG"),print_exec=True)
# print("Copy:",p.show_vars())
# p.execute(macro_bit_shift("#REG"))
# print("Bitshift",p.show_vars())
# p.execute(macro_add("#REG",var[2],var[2]))
# print("Add",p.show_vars())
# p.execute(macro_bit_shift("#REG"))
# print("Bitshift",p.show_vars())
# p.execute(macro_add("#REG",var[2],var[2]))
# print("Add",p.show_vars())
# p.execute(macro_bit_shift("#REG"))
# print("Bitshift",p.show_vars())
# p.execute(macro_add("#REG",var[2],var[2]))
# print("Add",p.show_vars())
# print(p.var_values())

