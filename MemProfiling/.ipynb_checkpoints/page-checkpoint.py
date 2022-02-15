'''
INFO
    This class is used to model a page it contains info about :
        1. Id of Page
        2. List of Request Ids e.g. if req_id = [1,3,5] it means that this page was requested in the 1st,3rd and 5th 
        Request in the sequence of Request generated by trafficGen
        3. reuse_dist reuse distances of a Page ,distance between every consecutive access
        4. Total number of times this page was misplaced during scheduling
        5. Periods/Scheduling intervals in which the page was misplaced
        6. Counts_ep number of accesses per epoch/interval e.g. [1,5,10,12] means that in the first interval the page 
        was accessed once ,in the second period it was access 5 times etc.
        7. loc_ep is the location of the page in each epoch/interval e.g. [0,1,1,0] means that in the first interval the page
        was located in DRAM ,then moved to NVM for the second epoch and so on.
        8. pred_counts is the number of predicted accesses in a scheduling interval which comes from either the history-scheduler 
        or hybrid scheduler 
        9. writesPerPeriod,readsPerPeriod self explanatory (#writes for every single period, #reads for every single period)
        10. misplacementsPeriods = list of periods this Page was misplaced
USE CASE 
    Can't be used alone ,it's used inside the other classes
    To obtain all these information classes further up in the abstraction layer - (profile,Page Selector, Scheduler) should be initiallized
'''

class Page:
    def __init__(self,id):
        self.id=id
        self.req_ids=[]
        self.pc_ids=[]
        self.address=0
        self.reuse_dist=[]
        self.misplacements=0
        self.misplacementsPeriods=[]
        self.writesPerPeriod=[]
        self.readsPerPeriod=[]
        self.oracle_counts_ep=0
        self.oracle_counts_binned_ep = []
        self.pred_counts_binned_ep = []
        self.counts_ep = []
        self.loc_ep = []
    
    def increase_cnt(self,ep):
        self.counts_ep[ep]+=1
    
    def writesPerEpoch(self,ep):
        self.writesPerPeriod[ep]+=1

    def readsPerEpoch(self,ep) :
        self.readsPerPeriod[ep]+=1