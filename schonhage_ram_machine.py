# -*- coding: utf-8 -*-
"""
Machines de Schonhage 1980
Machine RAM0
"""

def execute(program,ram0): 
    acc_z = 0
    addr_n = 0
    (program,labels)=parse(program)
    control = 0
    print("ctrl:",0," : ",program[0],": z = ",acc_z,":n = ", addr_n, " : ",ram0)
    while control < len(program):
        e=program[control]
        if   e =="Z":
            acc_z=0
        elif e== "A":
            acc_z+=1
        elif e== "N":
            addr_n=acc_z
        elif e== "L":
            acc_z=ram0[acc_z]
        elif e== "S": #store
            ram0[addr_n] = acc_z
        elif e== "C": #COM z=0?
            if not (acc_z == 0): 
                control +=1
                if program[control] == "G": control+=1
        elif e == "G": #goto 
            key = program[control+1]
            control = labels[key]-1 #parce que va être réincrémentéjuste après
        else:
            break
        control +=1
        print("ctrl:",control," : ",e,": z = ",acc_z,":n = ", addr_n, " : ",ram0)
    print ("Terminé")

def parse (program):
    d = {}
    i = 0
    while i < len(program):
        if program[i] == "X":
            d[program[i+1]]=i #assigne pos 1 au lbl 
            program = program[:i]+program[i+2:]
        i+=1
    return (program,d)

#exemples de programmes pour simuler la RAM1
lda_program = "ZANZAAAAS"
std_program = "ZAAAANZALS"
com_program = "ZALAAANZSZAAAALAAANSZALAAALCA"
# programme qui multliplie par 2 le nombre en <0>
mult2_program = "\
ZANSZLANS\
X1ZLLCG2G7\
X2ZANX3ASLCG4ZALG3\
X4ZALNS\
ZLANLASG1\
X7ZNLALS"
# X5ASLCG6ZLALG5\X6ZLALNSG1\
# explication du prg mult2
# marque la case 1 et la case x+1
# X1 : test principal
# si la case x est vide, G2
# sinon on a fini de compter, G7
# X2: cherche la première case vide et marque la:
## retourne à 0, avance à 1, fixe N=1
## X3: avance d'une case, et mémorise z en 1
## charge <z> et teste si  = 0?
## si oui X4
## sinon z = <1> retourne à X3
# X4: marque la nouvelle case z = <1> N = z , S
# cherche la première case vide et marque la
## fixe N = z = x+1, puis ajoute-y 1 
# retourne à X1
# X7 fixe N = 0, met z = x+1 (contient 2x) S
add_program  = ("ZLCG7"
                "X1ZLAALCG2G7"
                "X2ZAAN"
                "X3SLCG4ZAALAG3"
                "X4ZAALNS"
                "ZANLASG1"
                "X7Z")


ram_lda=[0]*20
ram_lda[1]=0
ram_lda[4]=6
#execute(lda_program,ram_lda)

ram_std=[0]*20
ram_std[1]=7
ram_std[4]=0
#execute(std_program,ram_std)

ram_com=[0]*20
ram_com[1]=10
ram_com[4]=10
#execute(com_program, ram_com)

ram_mult2=[0]*20
ram_mult2[0]=9
#execute(mult2_program,ram_mult2)

def add (x,y):
    add_program  = ("ZLCG7"
                    "X1ZLAALCG2G7"
                    "X2ZAAN"
                    "X3SLCG4ZAALAG3"
                    "X4ZAALNS"
                    "ZANLASG1"
                    "X7Z")
    #explication du prg add <1>=<0>+<1> x=<0>, y=<1>
    # si x=0 arrête toi
    # X1 : test principal
    # si la case x+2 est vide, G2
    # sinon on a fini de compter G7
    # X2 va en 2 marque N
    # X3 mémorise z en 2, et teste <z>=0? SLCG4ZAALAG3 sinon avance et recommence
    # X4 si vide marque: ZAALNS
    # incrémente y et reviens au début: ZANLASG1
    u = min(x,y)
    v = max(x,y)
    ram_add=[0]*(u+3)
    ram_add[0]=u
    ram_add[1]=v
    execute(add_program,ram_add)
    return ram_add[1]

print (add(3,5))
