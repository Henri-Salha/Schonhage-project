# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 10:32:04 2023
Schonhage SMM machines (Storage Modification Machines)
Based on Schonhage's 1980 paper
@author: Henri Stephanou
this file defines the general SMM class
"""

import networkx as nx

class SMM:
    def __init__(self,alphabet="LR",center=0):
        # creates an SMM machine with an alphabet and an initial center
        # which points to itself
        self.graph = nx.MultiDiGraph()
        self.graph.add_node(center)
        self.alphabet = alphabet
        self.center = center
        for i in alphabet:
            self.graph.add_edge(center,center,key=i)
    
    def execute(self,program,inpt="",print_exec=False,limit=10000):
        #program, input, prints log, limit nb of moves
        def print_cmd (instr):
            #formats the print-out of the executed cmd
            if instr[0]==0:
                a=' '*15 #labels
            else: 
                a = f'{instr[0]:<15}'
            b = f'{instr[1]:<5}'
            if len(instr)<3 or instr[2]==0:
                c='' #arg1
            else:
                c = f'{instr[2]:<8}'
            if len(instr)<4 or instr[3]==0:
                d='' #arg2
            else:
                d = f'{instr[3]:<8}'
            return a+b+c+d
        i = 0 #indexes the line of the program executed
        j = 0 #counts the number of cmds executed
        labels = [x[0] for x in program]
        while (i < len(program)) and (limit > j):
            j +=1
            instr = program[i]
            #print(f'{i:>4}',":",print_cmd(instr))
            if print_exec: print(j,":",print_cmd(instr))
            if instr[1]=="new":
                self.newG(instr[2],instr[3])
            if instr[1]=="set":
                self.setG(instr[2],instr[3])
            if instr[1]=="test":
                if not self.testG(instr[2],instr[3]): i +=1
            if instr[1]=="goto":
                i = labels.index(instr[2])- 1    
            if instr[1]=="input":
                if inpt != "": 
                    if inpt[0] == '0':
                        i = i = labels.index(instr[2])- 1    
                    elif inpt[0] == '1':
                        i = i = labels.index(instr[3])- 1    
                    inpt = inpt[1:]
            if instr[1]=="pass": pass
            i+=1
        #print(*list(self.graph.edges), sep='\n')
            
    def newG (self, word,newnode=""):
        # instruction new of Schonhage
        # reconfigure le graphe selon les termes de Schonhage
        if newnode == "": newnode = self.newnode_name()
        self.graph.add_node(newnode)
        if word != "":
            u = word[:-1] #le mot sans la dernière lettre
            a = word[-1:] #la dernière lettre du mot
            lastnode = self.find(self.center, word)
            beforelastnode = self.find(self.center, u)
            self.graph.remove_edge(beforelastnode,lastnode,a)
            self.graph.add_edge(beforelastnode,newnode,key=a)
        else:
            lastnode = self.center
            self.center = newnode
        for i in self.alphabet:
            self.graph.add_edge(newnode,lastnode,key=i)
            
    
    def setG (self, word1,word2):
        # instruction set of Schonhage
        # reconfigure le graphe selon les termes de Schonhage
        #center = list(graph.nodes)[0]
        targetnode = self.find(self.center,word2)
        if word1 != "":
            u = word1[:-1] #le mot sans la dernière lettre
            a = word1[-1:] #la dernière lettre du mot
            lastnode = self.find(self.center, word1)
            beforelastnode = self.find(self.center, u)
            self.graph.remove_edge(beforelastnode,lastnode,a)
            self.graph.add_edge(beforelastnode,targetnode,key=a)
        else:
            self.center = targetnode
        
    def testG(self,word1,word2):
        # function test of Schonhage
        return self.find(self.center,word1)==self.find(self.center,word2)
    
    
    def find (self,node,word):
        # gives the node pointed at by the word from node node
        if word =="": return node
        return self.find(self.hop(node,word[0]),word[1:])
        
    def hop (self,node,letter):
        # gives the node pointed at by the edge of label letter from node node
        i = next((x for x in list(self.graph.edges) if x[0]==node and x[2]==letter),node)
        return i[1]
    
    def newnode_name(self):
        #sélectionne un nouveau label pour le nouveau noeud
        llist = list(self.graph.nodes)
        fltr = [x for x in llist if type(x)==type(self.center)]    
        if type(self.center)==type('a'):
            if fltr == []: return 'a'
            return next_char(max(fltr))
        else:
            if fltr == []: return 1
            return max(fltr)+1

def next_char(char):
    #helper function
    return chr(ord(char)+1)