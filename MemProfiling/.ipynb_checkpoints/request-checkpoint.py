'''
    Request: Every line in trace file is treated as a request
    For every Request we have:
        id = unique number
        ep = Scheduling epoch a request belongs to
        op = operation (read or write)
        page_id = page id of page requested
        page_address = raw address of page
        loc = served by NVM or DRAM
'''

class Request:
    def __init__(self, id,op, page_id,page_address):
        self.id = id
        self.ep = 0
        self.op = op
        self.page_id = page_id
        self.page_address = page_address
        self.loc = -1
        
