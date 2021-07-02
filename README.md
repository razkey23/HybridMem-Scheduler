```python
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session
```


```python
import numpy
import matplotlib.pyplot as plt
import pandas
import math
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pylab as plt
numpy.random.seed(7)
```

# LSTM-INIT

## Traffic Handling


```python
'''
INPUT of Request : id , operation (r/w) , page_id

INPUT of TrafficGen : trace file name (with location)
Function :parse_trace() returns : 
    1. number of requests (num_reqs)
    2. number of pages (num_pages)
    3. list of requests with unique id,operation and page_id (integer from 1 to num_pages)
    4. dictiona
    ry of mapping page_id to pages (page_map)
    
Function plotter_page_locality() returns:
    A plot where:
        x-axis : Page in regards to the  
'''



class Request:
    def __init__(self, id,op, page_id,page_address):
        self.id = id
        self.ep = 0
        self.op = op
        self.page_id = page_id
        self.page_address = page_address
        self.loc = -1
        

#WHAT I NEED IS 
class TrafficGen():
    def __init__(self,trace_file):
        self.req_sequence = []
        self.num_pages = 0
        self.num_reqs = 0
        self.trace_file = trace_file
        self.page_map= {}
    
    def parse_trace(self):
        with open(self.trace_file,'r') as infile:
            seq=[]
            #page_map={}
            #counter=0
            for line in infile.readlines():
                row = line.split(" , ")
                row[2] = row[2][0:14]
                op=""
                if str(row[1])=="0x1":
                    op="w"
                else:
                    op="r"
                self.num_reqs+=1
                paddr = int(row[2],0)
                base_addr = paddr>>12
                #base_addr = paddr - (paddr % 4096)
                key = str(base_addr)
                page_id = self.num_pages
                if key not in self.page_map:
                    self.page_map[key] = self.num_pages #First Occurence of page
                    self.num_pages+=1
                    #counter+=1
                else :
                    page_id = self.page_map[key]
                req = Request(self.num_reqs -1 ,op,page_id,key)
                self.req_sequence.append(req)
    
    
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
                
                
            
        
    
```

## Memory handling/Profiling


```python
#Page class
class Page:
    def __init__(self,id):
        self.id=id
        self.req_ids=[]
        self.pc_ids=[]
        self.reuse_dist=[]
        self.misplacements=0
        self.oracle_counts_ep=0
        self.oracle_counts_binned_ep = []
        self.pred_counts_binned_ep = []
        self.counts_ep = []
        self.loc_ep = []
    
    def increase_cnt(self,ep):
        self.counts_ep[ep]+=1
```


```python
'''
    
    Can do the following with AddressSpace
    initiliaze it AddressSpace()
                    .populate(traffic)
                    (use it after initiating a scheduler)
    Get page_list[] for every Page I have the info 1.req_ids (array) 2.reuse distances 3. misplacements 4.oracle_counts_ep 
    
'''

class AddressSpace:
    def __init__(self):
        self.page_list=[]
        self.num_pages=[]
        self.reqs_l1_pages=[]
        self.l1_ratio=0
        self.l1_pages=0
        self.lru_list=[]
        self.policy=''
        self.oracle_page_ids=set()
        self.num_patterns = 0
        
    def set_patterns(self):
        distinct_page_cnts_seq = set()
        for page in self.page_list:
            #for every page in page list insert once (?)
            if str(page.oracle_counts_binned_ep) not in distinct_page_cnts_seq:
                distinct_page_cnts_seq.add(str(page.oracle_counts_binned_ep))
        self.num_patterns=len(distinct_page_cnts_seq)
        
    #Get the traffic and populate AddressSpace's data
    def populate(self,traffic):
        self.num_pages=traffic.num_pages
        #Initiliaze IDs
        for p_id in range(self.num_pages):
            page=Page(p_id)
            self.page_list.append(page)
        
        #Get requests per page
        for req in traffic.req_sequence:
            page = self.page_list[req.page_id]
            #Append to list the id of request
            page.req_ids.append(req.id)
         
        #Reuse distance for Every Page
        for page in self.page_list:
            page.reuse_dist = np.diff(np.array(page.req_ids))
            
    def init_cnts(self,num_periods,policy):
        for page in self.page_list:
            page.counts_ep = np.zeros(num_periods)
            page.loc_ep = np.zeros(num_periods)
            page.pred_counts_binned_ep =np.zeros(num_periods)
            page.misplacements = 0
        self.lru_list = [page.id for page in self.page_list]
        self.policy = policy 
        self.oracle_page_ids = set()
    
    #Dunno    
    def init_hybrid(self,oracle_page_ids):
        self.oracle_page_ids = set(oracle_page_ids)
    
    #INIT TIERING -Will check l8r
    def init_tier(self, l1_ratio):
        self.l1_ratio = l1_ratio
        self.l1_pages = int(l1_ratio * self.num_pages)
        idxs = range(self.num_pages)
        if self.l1_ratio == 1:
              self.tier_pages(idxs, [], 0)
        elif self.l1_ratio == 0:
              self.tier_pages([], idxs, 0)
        else:
            l1_tier, l2_tier = [], []
            for i in range(self.num_pages):
                if i % 2 == 0 and len(l1_tier) < self.l1_pages:
                      l1_tier.append(i)
                else:
                      l2_tier.append(i)
        self.tier_pages(l1_tier, l2_tier, 0)
   

    def tier_pages(self, l1_tier, l2_tier, ep):
        for page_id in l1_tier:
            page = self.page_list[page_id]
            page.loc_ep[ep] = 0
        for page_id in l2_tier:
            page = self.page_list[page_id]
            page.loc_ep[ep] = 1
            
    #Update LRU with page_id (pop from list and append it again)
    def update_lru(self,page_id):
        for idx in range(len(self.lru_list)):
            if self.lru_list[idx] == page_id:
                self.lru_list.pop(idx)
                break
        self.lru_list.append(page_id)
        
    def update_tier(self,curr_ep):
        for page in self.page_list:
            page.loc_ep[curr_ep] = page.loc_ep[curr_ep-1]
            
    def get_l2_hot_pages(self,curr_ep,policy):
        sorted_hot_page_ids=[]
        hot_page_ids=[]
        hot_page_cnts = [] 
        for page in self.page_list:
            pcnt = 0 
            if policy == 'history' :
                pcnt = page.oracle_counts_binned_ep[curr_ep-1]
            elif policy == 'oracle':
                pctn = page.oracle_counts_binned_ep[curr_ep]
            elif policy == 'hybrid' or policy == 'hybrid-group':
                if page.id in self.oracle_page_ids: 
                    pcnt = page.oracle_counts_binned_ep[curr_ep] #Oracular Predictions
                else: 
                    pcnt = page.oracle_counts_binned_ep[curr_ep-1] #History Predictions
            if pcnt !=0: #Touched pages in this period
                hot_page_ids.append(page.id)
                hot_page_cnts.append(pcnt)
            page.pred_counts_binned_ep[curr_ep] = pcnt
            
        sorted_idxs = np.argsort(hot_page_cnts)[::-1]
        sorted_hot_page_ids = [hot_page_ids[i] for i in sorted_idxs]
        npages=0
        page_id=0
        l2_hot_pages_to_move = []
        while npages < self.l1_pages and npages < len(sorted_hot_page_ids):
            page = self.page_list[sorted_hot_page_ids[page_id]]
            if page.loc_ep[curr_ep-1]==1:
                l2_hot_pages_to_move.append(page.id)
                if page.pred_counts_binned_ep[curr_ep] != page.oracle_counts_binned_ep[curr_ep]:
                    page.misplacements +=1
            npages+=1
            page_id+=1
        return l2_hot_pages_to_move
        
    def get_l1_lru_pages(self,curr_ep):
        lru_page_ids = []
        for page_id in self.lru_list:
            page = self.page_list[page_id]
            if page.loc_ep[curr_ep-1]==0:
                lru_page_ids.append(page.id)
        return lru_page_ids
        
        
    def capacity_check(self,curr_ep):
        l1_pages=0
        for page in self.page_list :
            if page.loc_ep[curr_ep]==0:
                l1_pages+=1
        percentage = l1_pages / float(self.num_pages)
        if percentage > self.l1_ratio:
            print("Error capacity ratio is",perc,"insted of ",self.l1_ratio)
            
       #PAGE REUSE HISTOGRAM ++
    

```

## Scheduler Implementation


```python
class Scheduler:
    def __init__(self):
        self.policy =''
        self.memory=None
        self.traffic=None
        self.num_reqs_per_ep=0
        self.curr_ep=0
        self.num_migr=0
        self.l1_hits=0
        
    def init(self,traffic,memory,policy,num_reqs_per_ep,l1_ratio):
        self.traffic=traffic
        self.memory=memory
        self.policy=policy
        self.num_reqs_per_ep=num_reqs_per_ep
        if num_reqs_per_ep == 0 :
            self.num_periods=1
        else:
            self.num_periods=int(traffic.num_reqs/num_reqs_per_ep)+1
        self.l1_ratio=l1_ratio
        self.curr_ep=0
        self.num_migr=0
        self.l1_hits=0
        self.memory.init_cnts(self.num_periods,policy)
        self.memory.init_tier(self.l1_ratio)
        self.set_oracle_cnts()
        self.memory.set_patterns()
        print("[Scheduler] Initialization done for policy =", self.policy, "periods =", self.num_periods, "reqs per period =", self.num_reqs_per_ep, "cap ratio =", self.l1_ratio)
        
    def set_oracle_cnts(self):
        for page in self.memory.page_list:
            page.oracle_counts_ep = np.zeros(self.num_periods)
        ep=0
        for req in self.traffic.req_sequence:
            if self.num_reqs_per_ep > 0:
                if req.id % self.num_reqs_per_ep == 0 and req.id !=0:
                    ep +=1  #EPOCH SWITCH
            page = self.memory.page_list[req.page_id]
            page.oracle_counts_ep[ep]+=1
            
        for page in self.memory.page_list:
            bins = range(0,int(max(page.oracle_counts_ep)),20)
            idxs = np.digitize(page.oracle_counts_ep,bins)
            page.oracle_counts_binned_ep = [bins[idxs[i]-1] for i in range(len(page.oracle_counts_ep))]
            
    def run(self):
        for req in self.traffic.req_sequence:
            if self.num_reqs_per_ep > 0 :
                if req.id % self.num_reqs_per_ep == 0 and req.id != 0:
                    self.retier()
            page=self.memory.page_list[req.page_id]
            page.increase_cnt(self.curr_ep)
            self.memory.update_lru(page.id)
        self.hitrate()
        
    def retier(self):
        self.memory.capacity_check(self.curr_ep)
        self.curr_ep+=1
        self.memory.update_tier(self.curr_ep)
        hot_pages = self.memory.get_l2_hot_pages(self.curr_ep,self.policy)
        nmigr = min(self.memory.l1_pages,len(hot_pages))
        lru_pages = self.memory.get_l1_lru_pages(self.curr_ep)
        self.memory.tier_pages(hot_pages[:nmigr],lru_pages[:nmigr],self.curr_ep)
        self.num_migr += 2*nmigr
        
    def hitrate(self):
        for page in self.memory.page_list:
            for ep in range(self.num_periods):
                if page.loc_ep[ep]==0:
                    self.l1_hits+=page.counts_ep[ep]
```

## Profile / Inits


```python
class Profile:
    def __init__(self, trace_file):
        self.trace_file = trace_file
        self.traffic = TrafficGen(self.trace_file)
        self.hmem = AddressSpace()
        self.scheduler = Scheduler()
    
    def __init__(self, trace_file):
        self.trace_file = trace_file
        self.traffic = TrafficGen(self.trace_file)
        self.hmem = AddressSpace()
        self.scheduler = Scheduler()
  
    def init(self):
        self.traffic.parse_trace()
        #self.traffic.print_traffic_sum()
        self.hmem.populate(self.traffic)
```

## Performance model


```python
import csv

class Platform:
    def __init__(self,name,local_lat,rem_lat,local_bw,rem_bw,period_cost,migr_cost):
        self.name = name
        self.local_lat = local_lat
        self.rem_lat = rem_lat
        self.local_bw = local_bw
        self.rem_bw = rem_bw
        self.period_cost = period_cost
        self.migr_cost = migr_cost
    
class PerfModel:
    
    def __init__(self, prof, platform_name, policy, cap_ratio, num_reqs):
        self.profile = prof
        self.platform_name = platform_name
        self.platform = None
        self.policy = policy
        self.cap_ratio = cap_ratio
        self.num_reqs_per_period = num_reqs
        self.stats = {}
    
    def init(self):
        self.set_platform()
        self.profile.scheduler.init(self.profile.traffic,self.profile.hmem,self.policy,self.num_reqs_per_period,self.cap_ratio) #CALL THE SCHEDULER
        
    def init_hybrid(self,oracle_page_ids):
        self.profile.hmem.init_hybrid(oracle_page_ids)
        
    def set_platform(self):
        fast_lat=50
        fast_bw=10
        period_cost = 3000
        migr_cost = 1000
        if self.platform_name == 'Fast:NearFast':
            self.platform = Platform('Fast:NearFast', fast_lat, 2.2 * fast_lat, fast_bw, fast_bw, period_cost, migr_cost)
        elif self.platform_name == 'Fast:NearSlow':
            self.platform = Platform('Fast:NearSlow', fast_lat, 3 * fast_lat, fast_bw, 0.37 * fast_bw, period_cost, migr_cost)  # 2.7x slower BW
        elif self.platform_name == 'Fast:FarFast':
            self.platform = Platform('Fast:FarFast', fast_lat, 1000 + 2.2 * fast_lat, fast_bw, 0.1 * fast_bw, period_cost, migr_cost)  # 10x slower BW
        elif self.platform_name == 'Fast:FarSlow':
            self.platform = Platform('Fast:FarSlow', fast_lat, 1000 + 3 * fast_lat, fast_bw, 0.1 * fast_bw, period_cost, migr_cost)  # 10x slower BW 
        
    def run(self):
        self.profile.scheduler.run()
        #self.compute_baselines()
        #self.compute_perf()
        #self.compute_other_metrics()
        
    #METRICS HERE
    
```

## Page Selector


```python
class PageSelector:
    def __init__(self,prof,platform_name,cap_ratio,num_reqs_per_ep,resdir_prefix):
        self.prof=prof
        self.platform_name = platform_name
        self.cap_ratio = cap_ratio
        self.num_reqs_per_ep = num_reqs_per_ep
        self.solution=''
        self.resdir_prefix=resdir_prefix
    
    def get_misplaced_pages_sim(self):
        page_ids = []
        for page in self.prof.hmem.page_list :
            if page.misplacements > 0 :
                page_ids.append(page.id)
        return page_ids
    
    def get_misplaced_pages(self):
        self.run_scheduler('history',[],0)
        page_ids = []
        for page in self.prof.hmem.page_list :
            if page.misplacements > 0:
                page_ids.append(page.id)
        return page_ids
    
    def get_distinct_access_pattern(self,page_ids):
        distinct_page_cnts_seq = set()
        for page_id in page_ids:
            page = self.prof.hmem.page_list[page_id]
            if str(page.oracle_counts_binned_ep) not in distinct_page_cnts_seq:
                distinct_page_cnts_seq.add(str(page.oracle_counts_binned_ep))
        return distinct_page_cnts_seq
    
    def select_k_page_groups(self,ordered_page_ids,k):
        selected_page_ids =[]
        selected_patterns = set()
        for page_id in order_page_ids:
            if str(page.oracle_counts_binned_ep) not in selected_patterns and len(selected_patterns) < k:
                selected_patterns.add(str(page.oracle_counts_binned_ep))
            if str(page.oracle_counts_binned_ep) in selected_patterns:
                selected_page_ids.append(page_id)
        return selected_page_ids
    
    def get_ordered_pages(self,page_ids):
        benefit_per_page=[]
        for id in page_ids :
            page = self.prof.hmem.page_list[id]
            benefit = sum(page.oracle_counts_binned_ep)*page.misplacements
            benefit_per_page.append(benefit)
        sorted_idxs = np.argsort(benefit_per_page)[::-1]
        ordered_page_ids = [page_ids[i] for i in sorted_idxs]
        return ordered_page_ids
    
    def run_scheduler(self,policy,selected_pages_for_oracle,num_rnns):
        sim=PerfModel(self.prof,self.platform_name,policy,self.cap_ratio,self.num_reqs_per_ep)
        sim.init()
        if policy == 'hybrid' or policy == 'hybrid-group':
            sim.init_hybrid(selected_pages_for_oracle)
        sim.run()
        
```


```python
import matplotlib.pylab as plt
trace_file='/kaggle/input/rodinia/backprop0'
prof = Profile(trace_file)
prof.init()
  
  # Convert to per page access counts
sim = PerfModel(prof, 'Fast:NearSlow', 'history', 0.2, 35650) 
sim.init()
sim.run()
#prof = Profile(trace_file)
pgs = PageSelector(prof, 'Fast:NearSlow', '0.2', 35650,'')
pages_misplaced = pgs.get_misplaced_pages_sim()
pages_ordered = pgs.get_ordered_pages(pages_misplaced)
#traffic = TraffiGen(trace_file)
#asd = traffic.parse_trace()
#hmem = AddressSpace()
#hmem.populate(traffic)
#scheduler = Scheduler()
#traffic.plotter_page_operations()

#print(traffic.num_reqs,traffic.num_pages)
#sequence = traffic.req_sequence

#print(traffic.num_pages)
```

    [Scheduler] Initialization done for policy = history periods = 15 reqs per period = 35650 cap ratio = 0.2
    


    ---------------------------------------------------------------------------

    KeyboardInterrupt                         Traceback (most recent call last)

    <ipython-input-10-9cea9e1cdb9a> in <module>
          7 sim = PerfModel(prof, 'Fast:NearSlow', 'history', 0.2, 35650) # cori's frequency, so that less periods for RNN training
          8 sim.init()
    ----> 9 sim.run()
         10 #prof = Profile(trace_file)
         11 pgs = PageSelector(prof, 'Fast:NearSlow', '0.2', 35650,'')
    

    <ipython-input-7-ca9fc3a1c41e> in run(self)
         44 
         45     def run(self):
    ---> 46         self.profile.scheduler.run()
         47         #self.compute_baselines()
         48         #self.compute_perf()
    

    <ipython-input-5-b7bd28215d01> in run(self)
         51             page=self.memory.page_list[req.page_id]
         52             page.increase_cnt(self.curr_ep)
    ---> 53             self.memory.update_lru(page.id)
         54         self.hitrate()
         55 
    

    <ipython-input-4-8151028f0f5e> in update_lru(self, page_id)
         91     def update_lru(self,page_id):
         92         for idx in range(len(self.lru_list)):
    ---> 93             if self.lru_list[idx] == page_id:
         94                 self.lru_list.pop(idx)
         95                 break
    

    KeyboardInterrupt: 



```python
print(pages_ordered)
```
