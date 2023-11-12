# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 22:43:57 2023

@author: henri
"""

import schonhage_ram_machine as ram
import_schonhage_smm_machine as smm

class SMM_RAM(smm.SMM):
    def __init__(self,ram_memory,z_acc=0,n_addr=0):#ram_memory est le contenu des 
    #initializes SMM machine with the initial tape of the RAM machine to be interpreted
        self.graph = nx.MultiDiGraph()
        self.graph.add_node('c')
        self.alphabet = "AB"
        self.center = 'c'
        self.graph.add_edge('c','a',key='B')
        self.graph.add_edge('c',0,key='A')        
        self.graph.add_edge('a',z_acc,key='A')#z
        self.graph.add_edge('a',n_addr,key='B')#n
        if len(ram_memory)<max(ram_memory):#prolonge la mémoire
        # pour que tout puisse être bien référencé
            ram_memory+=[0]*(max(ram_memory)+1-len(ram_memory))
        for i in range(0,len(ram_memory)):
            self.graph.add_edge(i,i+1,key='A')
        for i in range(0,len(ram_memory)):
            self.graph.add_edge(i,ram_memory[i],key='B')
        self.graph.add_edge(i+1,0,key='A')
        self.graph.add_edge(i+1,0,key='B')
        
    def newnode_name(self):
        #selects new node name (+1)
        return self.max_node()+1

    def max_node(self):
        #looks for the largest node (of RAM memory)
        llist = list(self.graph.nodes)
        fltr = [x for x in llist if type(x)==type(1)]    
        if fltr == []: return 0
        return max(fltr)
    
    def execute(self,program):
        #RAM0 Machine interpreter. Takes a RAM0 program as input.
        (program,labels)=ram.parse(program)
        control = step = 0
        while control < len(program):
            e=program[control]
            if   e =="Z":
                self.setG("BA","A")
            elif e== "A":
                t = self.testG("BAA","A")
                if t: self.newG("BAA")
                self.setG("BA","BAA")
            elif e== "N":
                self.setG("BB","BA")
            elif e== "L":
                self.setG("BA","BAB")
            elif e== "S": #store
                self.setG("BBB","BA")
            elif e== "C": #COM z=0?
                if not self.testG("BA","A"):
                    control +=1
                    if program[control] == "G": control+=1
            elif e == "G": #goto 
                key = program[control+1]
                control = labels[key]-1 #parce que va être réincrémentéjuste après
            else:
                break
            control +=1
            # next lines emulates the RAM0 program as a complimentary check
            acc_z = self.hop('a','A')
            addr_n = self.hop('a','B')
            ram0=[self.hop(i,'B') for i in range(0,self.max_node())]
            print("ctrl:",control," : ",e,": z = ",acc_z,":n = ", addr_n, " : ",ram0)
            #next lines to enable to have graphs for each step
            #step +=1
            #self.draw(step)
        print ("Done")
    
    def draw(self,fig=1):
        #draws the SMM machine current state
        plt.figure(fig)
        def color_edge(x):
            if x == 'A': return "tab:orange"
            return "tab:blue"
        edge_nodes = set(self.graph) - {'a','c'}
        pos = nx.circular_layout(self.graph.subgraph(edge_nodes))
        pos['c'] = np.array([-0.25,-0.25])
        pos['a']= np.array([0.25,0.25])
        colors = [color_edge(x[2]) for x in list(self.graph.edges)]
        nx.draw(self.graph, pos, edge_color = colors, with_labels=True)        

# basic SMM machine example
# g = SMM("LR",0)
# g.newG("R")
# g.newG("RR")
# g.newG("RRR")
# g.newG("RRRR")
# g.setG("RL","")
# g.setG("RRL","R")
# g.setG("RRRL","RR")
# g.setG("RRRRL","RRR")
# g.setG("RRRRR","RRRR")
# a = list(g.graph.edges)
# t = g.testG("RRR","RRRRRLLL")
#nx.draw(g.graph)

# h = SMM_RAM([2,5])
# h.draw(1)
# h.execute(ram.add_program)
# h.draw(2)