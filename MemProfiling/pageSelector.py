'''
    INFO
        This class models the PageSelector. Mainly used to obtain info about 
        1. misplaced pages
        2. Sort Misplaced pages benefit-wise
        And it is also used to run the whole simulation and the scheduler (Higher Level Class)
        
'''
from trafficGen import *
from page import *
from addressSpace import *
from scheduler import *
from profile import *
from performanceModel import *

class PageSelector:
    def __init__(self,prof,platform_name,cap_ratio,num_reqs_per_ep,resdir_prefix):
        self.prof=prof
        self.platform_name = platform_name
        self.cap_ratio = cap_ratio
        self.num_reqs_per_ep = num_reqs_per_ep
        self.solution=''
        self.resdir_prefix=resdir_prefix
    
    # RETURN Pages misplaced using current scheduler
    def get_misplaced_pages_sim(self):
        page_ids = []
        for page in self.prof.hmem.page_list :
            if page.misplacements > 0 :
                page_ids.append(page.id)
        return page_ids
    
    # RUN HISTORY SCHEDULER TO FIND MISPLACED PAGES
    def get_misplaced_pages(self):
        self.run_scheduler('history',[],0)
        page_ids = []
        for page in self.prof.hmem.page_list :
            if page.misplacements > 0:
                page_ids.append(page.id)
        return page_ids
    
    '''
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
        for page_id in ordered_page_ids:

            if str(page.oracle_counts_binned_ep) not in selected_patterns and len(selected_patterns) < k:
                selected_patterns.add(str(page.oracle_counts_binned_ep))
            if str(page.oracle_counts_binned_ep) in selected_patterns:
                selected_page_ids.append(page_id)
        return selected_page_ids
    '''
    
    # ORDER PAGES BY PROFIT FACTOR
    def get_ordered_pages(self,page_ids):
        benefit_per_page=[]
        for id in page_ids :
            page = self.prof.hmem.page_list[id]
            benefit = sum(page.oracle_counts_binned_ep)*page.misplacements
            benefit_per_page.append(benefit)
        sorted_idxs = np.argsort(benefit_per_page)[::-1]
        ordered_page_ids = [page_ids[i] for i in sorted_idxs]
        return ordered_page_ids
    
    # RUN THE SCHEDULER 
    def run_scheduler(self,policy,selected_pages_for_oracle,num_rnns):
        sim=PerformanceModel(self.prof,self.platform_name,policy,self.cap_ratio,self.num_reqs_per_ep)
        sim.init()
        if policy == 'hybrid' or policy == 'hybrid-group':
            sim.init_hybrid(selected_pages_for_oracle)
        sim.run()