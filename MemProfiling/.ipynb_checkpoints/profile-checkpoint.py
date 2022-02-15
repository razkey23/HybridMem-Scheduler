'''
    Profile is used as an auxiliary class used to batch all the trivial commands needed to initiliaze
    scheduling e.g. parsing the trace ,populating the AddressSpace,and initiliazing a Scheduler

'''

from trafficGen import *
from page import *
from addressSpace import *
from scheduler import *

class Prof:
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
        self.hmem.populate(self.traffic) 