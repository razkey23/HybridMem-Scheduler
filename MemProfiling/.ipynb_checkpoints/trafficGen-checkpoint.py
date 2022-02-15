'''
INFO
    First layer of our "Profiling".

        * TrafficGen class is used to parse the raw input file and model the page accesses as a sequence
        of requests. TrafficGen only requires the input file and then we can get info about every single request that was made

USED AS
    trace_file ='/content/drive/MyDrive/Colab Notebooks/backprop0'
    traffic = TrafficGen(trace_file)
    parse = traffic.parse_trace()
    ...
    traffic.plotter_page_locality()

'''


import matplotlib.pyplot as plt
import pandas
import math
import numpy as np
from request import *

class TrafficGen():
    def __init__(self,trace_file):
        self.req_sequence = []
        self.num_pages = 0
        self.num_reqs = 0
        self.trace_file = trace_file
        self.page_map= {}
    
    def parse_trace(self):
        with open(self.trace_file,'r') as infile:
            for line in infile.readlines():
                row = line.split(" , ")
                row[3] = row[3][0:14]
                op=""
                if str(row[2])=="0x1":
                    op="w"
                else:
                    op="r"
                self.num_reqs+=1
                paddr = int(row[3],0)
                #base_addr = paddr>>12
                base_addr = paddr - (paddr % 4096)
                key = str(base_addr)
                page_id = self.num_pages
                if key not in self.page_map:
                    self.page_map[key] = self.num_pages #First Occurence of page
                    self.num_pages+=1
                else :
                    page_id = self.page_map[key]
                req = Request(self.num_reqs -1 ,op,page_id,key)
                self.req_sequence.append(req)
    
    
    
    
    '''
        The following plotters are not required for running the Simulator.
        They were used for analysis and further understanding of the trace
    '''
    
    # UTILITY PLOTTERS FOR TRAFFIC
    def plotter_page_locality(self):
        # Every page is sorted using and ID
        # X axis pageid locally - y axis #Occurencies
        page_occurencies={}
        l=sorted(list(self.page_map.keys()))
        newDict = { i : l[i] for i in range(0, len(l) ) }
        for i in range(len(l)):
            newDict[l[i]]=i
            
        for request in self.req_sequence:
            #page_nr = (int(request.page_address)-int(l[0]))>>12
            page_nr = newDict[request.page_address]
            #print(page_nr)
            #break
            if page_nr in page_occurencies:
                page_occurencies[page_nr]+=1
            else:
                page_occurencies[page_nr]=1
        #Convert dictionary to lists for plotter
        lists = sorted(page_occurencies.items())
        x, y = zip(*lists) # unpack a list of pairs into two tuples
        plt.plot(x, y)
        plt.show()
    
    def plotter_page_operations(self):
        reads=0
        writes=0
        for request in self.req_sequence:
            if request.op == 'r':
                reads+=1
            else:
                writes+=1
        x=["reads","writes"]
        y=[reads/self.num_reqs,writes/self.num_reqs]
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.bar(x,y)
        plt.show()
    
    # % of total pages per % of requests
    def plotter_page_occurence(self):
        #Total pages in self.num_pages
        pages_seen=0
        pages=set()
        dic={}
        percentage_seen=0
        counter=0
        for request in self.req_sequence:
            if request.page_id not in pages:
                pages.add(request.page_id)
                pages_seen+=1
            percentage_seen=pages_seen/self.num_pages
            dic[counter/self.num_reqs]=percentage_seen
            counter+=1
        lists = sorted(dic.items())
        x, y = zip(*lists) # unpack a list of pairs into two tuples
        plt.plot(x, y)
        plt.show()