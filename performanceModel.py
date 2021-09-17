'''
INFO 
    The platform class is used to initiliaze basic performance data of the simulated Platform
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