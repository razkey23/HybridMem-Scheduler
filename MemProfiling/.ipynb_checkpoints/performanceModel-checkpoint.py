'''
INFO 
    The PerfModel takes as input 
        1. Profile (that's why Profile should be initiliazed before calling PerfModel)
        2. Platform name
        3. Policy
        4. DRAM/NVM ratio
        5. Number of Requests Per Interval

'''
from trafficGen import *
from page import *
from addressSpace import *
from scheduler import *
from profile import *
import csv


class PerformanceModel:    
    def __init__(self, prof, platform_name, policy, cap_ratio, num_reqs):
        self.profile = prof
        self.platform_name = platform_name
        self.platform = None
        self.policy = policy
        self.cap_ratio = cap_ratio
        self.num_reqs_per_period = num_reqs
        self.stats = {}
    
    def init(self):
        self.profile.scheduler.init(self.profile.traffic,self.profile.hmem,self.policy,self.num_reqs_per_period,self.cap_ratio) #CALL THE SCHEDULER
        
    def init_hybrid(self,dic):
        self.profile.hmem.init_hybrid(dic)
        
    def run(self):
        self.profile.scheduler.run()