# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 10:05:52 2023
Schonhage SMM machines (Storage Modification Machines)
Based on Schonhage's 1980 paper
@author: Henri Stephanou
this file defines the B-scale SMM machine
used for the multiplication algorithm
"""
import schonhage_smm_machine as smm
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class SMM_Bscale(smm.SMM):
    def __init__(self,b=2,var=1):
        # creates an SMM machine with an alphabet and an initial center
        # which points to itself
        self.graph = nx.MultiDiGraph()
        self.alphabet = "PQSWZ"
        self.graph.add_node('A')
        self.center = 'A' #creates basic nodes
        for i in self.alphabet:
            self.graph.add_edge(self.center,self.center,key=i)
        #B scale creation
        self.b = b
        self.B = 2**b #B-scale
        prg = []
        for i in range(0,self.B):
            prg.append((0,"new","W"+"S"*i,i))
        prg.append((0,"set","W"+"S"*self.B,"W"))
        # prg.append((0,"new","WS",0))
        # prg.append((0,"set","W","S"))
        # prg.append((0,"set","S",""))
            #self.newG("WS",i)
        smm.SMM.execute(self,prg,print_exec=False) #can't use own exec function because free pointers not yet defined
        prg = [] # edges P and Q
        prg = [(0,"set","WP","W"),#traite le cas 0
               (0,"set","WQ","W"),
               (0,"set","P","WS"),#P comme compteur, va directement à 1
               (1,"set","Q","W"),#Q comme compteur
               (0,"set","PP","P"),#PP comme cible
               (2,"set","Q","QS"), # inc Q
               (0,"set","PP","PPS"), # inc PP
               (0,"test","PP","W"), #teste si atteint le bout
               (0,"goto",7,0),
               (0,"test","Q","P"), #teste si a doublé
               (0,"goto",3,0),
               (0,"goto",2,0),
               (3,"set","PPQ","P"),#flèche inverse
               (0,"set","PPSQ","P"),
               (0,"set","P","PS"),
               (0,"goto",1,0),
               (7,"set","PP",""),
               (0,"set","Q",""),#nettoie les compteurs
               (0,"set","P","")]
        smm.SMM.execute(self,prg,print_exec=False)
        #creation of variables anchor node V 
        prg = [(0,"new","Z","V")]
        for i in self.alphabet:
            prg.append((0,"set",f'Z{i}',"Z")) 
        smm.SMM.execute(self,prg,print_exec=False)
        # creation of variables
        self.nbvar=0 # increment par la fct newvar
        for i in range(0,var+1): #1 hidden variable
            self.new_var()
        self.vars=["Z"*(i+3) for i in range(var)]
        self.vars.reverse()
        self.register="ZZ"
        # assignation of free pointers
        self.free_pointers=["P","ZP","ZQ","ZW"]
        self.used_pointers=[]
        
    def new_var(self):
        name = "V"+str(self.nbvar)
        self.nbvar +=1
        prg = [(0,"new","ZZ",name),
               (0,"set","ZZW","ZZ"),#pointe vers lui-même par W initialement
               #(0,"set","ZZZ","Z") #la structure reboucle vers le QG 
               ]
        for i in range(0,self.b):#creation of bx binary digits
            prg += [(0,"new","ZZS",name+f'b{i}'),
                    (0,"set","ZZSP","ZZ"), #B-valeur à 0 #par convention 0= pointe sur Vx, 1 = pointe sur lui-même
                    (0,"set","ZZSQ","ZZ")
                    ] #carry à 0        
        for i in range(1,self.b+1): 
            prg += [(0,"set","ZZ"+"S"*i+"W","ZZ"+"S"*(i-1))]
        prg += [(0,"set","ZZ"+"S"*(self.b+1),"ZZ"),#B0 revient à la var
                (0,"set","ZZW","ZZ"+"S"*self.b),#V0 W pointe sur B0
                (0,"set","ZZWZ","ZZ"),
                (0,"set","ZZWQ","ZZ"),
                (0,"set","ZZP","W"),#valeur B-scale initalisées à 0
                (0,"set","ZZQ","W")] #carry initialisée à 0
        smm.SMM.execute(self,prg)
        
    def execute(self,program,inpt="",print_exec=False,limit=10000):
        program1 = self.parse(program)
        smm.SMM.execute(self,program1,inpt,print_exec,limit)
        self.free_pointers+=self.used_pointers #garbage collector
        self.used_pointers=[]
        return 
    
    def parse(self,program):
        #before calling standard SMM execute, parses variables using the machine free pointers
        d = dict() #allocateur de mémoire
        d["#REG"] = self.register 
        i = 0
        while i < len(program):
            #identifies all declarations in the program and allocates pointers
            if program[i][1]=="decl":
                decl_instr = program.pop(i)
                var_list = decl_instr[2:]
                for var in var_list:
                    d[var]=self.free_pointers.pop()
                    print("Using ", d[var], "pointing to", self.find('A',d[var]), "for v",var)
                    self.used_pointers.append(d[var])
                    if len(self.free_pointers)==1: 
                        print("expanding free pointers")
                        self.expand_pointers()
            i+=1
        print("Dictionary",d)
        for i in range(len(program)):
            #substitutes variable names with real pointer names
            for var in d.keys():
                #checks all arguments in each program line for all variable names
                if type(program[i][2])==str and var in program[i][2]:
                    instr = list(program[i])
                    program[i]= (instr[0],instr[1],instr[2].replace(var,d[var]),instr[3])
                if type(program[i][3])==str and var in program[i][3]:
                    instr = list(program[i])
                    program[i]= (instr[0],instr[1],instr[2],instr[3].replace(var,d[var]))
        #print("program:",*program, sep='\n')
        return program
    
    def expand_pointers(self):
        #creates a new node from a free pointer and adds all created pointers to the free pointer list
        ptr = self.free_pointers.pop(0)
        self.newG(ptr,"PTR_"+ptr)
        for i in self.alphabet:
            self.setG(ptr+i,ptr)
        self.free_pointers += [ptr+i for i in self.alphabet]
            
            
    
    def show_vars(self):
        nodes = [self.find(self.center,path) for path in self.vars]+['V3']
        return [str(self.hop(x,'Q'))+'.'+str(self.hop(x,'P')) for x in nodes]
    
    def var_values(self):
        #outputs decimal values of vars content
        nodes = [self.find(self.center,path) for path in self.vars]
        return [self.hop(x,'Q')*self.B+self.hop(x,'P') for x in nodes]
        
    
    def draw(self,fig=1):
        #draws the SMM machine current state
        plt.figure(fig)
        pos = dict()
        for i in range(0,self.nbvar):
            for j in range(0,(self.b//2)):
                k = self.b-j-1
                pos[f'V{i}b{j}']= np.array([self.B-1-i*4,+1.5+j*.5])
                pos[f'V{i}b{k}']= np.array([self.B+1-i*4,+1.5+j*.5])
            if self.b%2 == 1:
                k = self.b//2
                pos[f'V{i}b{k}']= np.array([self.B-i*4,+1.5+k*.5])
            pos[f'V{i}']=np.array([self.B-i*4,+1])
        pos['A'] = np.array([0,0])
        pos['V'] = np.array([0,0.5])
        for i in range(0,self.B):
                pos[i] = np.array([i+1,0])
        def color_edge(x):
            if x == 'W': return 'w'
            if x == 'S': return 'b'
            if x == 'P': return 'g'
            return 'm'
        colors = [color_edge(x[2]) for x in list(self.graph.edges)]
        nx.draw(self.graph, pos, edge_color = colors, with_labels=True)
