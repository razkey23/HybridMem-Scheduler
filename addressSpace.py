'''
INFO
    This class is used to create the addressSpace of our benchmark.It uses the generated traffic
    and it's used for analyzing the whole AddressSpace. It's used to 
     * Initiliaze page_ids
     * Get Requests per Page
     * Find Reuse of every Page
     * Tiering the Pages according to the policy (will be used later in the scheduler.py)
        Check -> get_l1_lru_pages,get_l2_hot_pages,tier_pages to see exactly how tiering happens
        LRU-List is kept for pages in DRAM. Hot pages in NVM switch places with those in lru list.
        Hot pages in NVM is found through l2_hot_pages.

'''



from trafficGen import *
from page import *

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
            page.misplacementsPeriods=[]
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
        pcnt=[]
        i=0
        for page in self.page_list:
            if policy == 'history' :
                pcnt.append(page.oracle_counts_binned_ep[curr_ep-1])
            elif policy == 'oracle':
                #print("IN HERE")
                pcnt.append(page.oracle_counts_binned_ep[curr_ep])
            elif policy == 'hybrid' or policy == 'hybrid-group':
                if page.id in self.oracle_page_ids: 
                    pcnt.append(page.oracle_counts_binned_ep[curr_ep]) #Oracular Predictions  
                else: 
                    pcnt.append(page.oracle_counts_binned_ep[curr_ep-1]) #History Predictions
                    
            if pcnt[i] != 0: #Touched pages
                hot_page_ids.append(page.id)
                hot_page_cnts.append(pcnt[i])
            page.pred_counts_binned_ep[curr_ep] = pcnt[i]
            i+=1
            
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
                    page.misplacementsPeriods.append(curr_ep)
            npages+=1
            page_id+=1
        #print(l2_hot_pages_to_move)
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
            print("Error capacity ratio is",perc,"instead of ",self.l1_ratio)