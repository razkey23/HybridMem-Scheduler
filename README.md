# Project Summary
## Introduction
### The problem
Main purpose of this project is to obtain information about the estimated performance that could be achieved
through different page-scheduling approaches in Hybrid Memory systems. During a program's runtime a lot of (4KB) Pages are accessed. These pages are located either in DRAM (Fast Access Memory) or in Persistent Memory (NVM) provided that the host machine has both DRAM and NVM kits. The access (either Read or Write) cost of a page differs between DRAM and NVM. This Non-Uniform access cost leaves a lot of room for performance optimization. Ideally we would have all the hot-pages (pages frequently accessed during runtime) in DRAM and cold Pages (rarely accessed pages in NVM) , but clustering pages between hot and cold is not an easy task. Hot pages in the beginning of the program might "turn" cold later , and vice versa. Therefore, we need to cluster pages during runtime ,using a scheduler. The scheduler will determine which pages are hot and which are cold at a given time-interval. Main purpose of the scheduler is to place the pages as efficiently as possible. The scheduler could be either implemented using a naive approach like history-scheduling (Pages that were accessed x times in the previous interval, will be accessed again x times ) or maybe a more sophisticated approach using Machine-Learning techniques.
### The Project
What this project currently achieves is , profiling memory traces collected from well-known benchmakrs suites such as Rodinia3.0 and PARSEC. This profiling includes some of the following   
    1. How DRAM/NVM capacity ratio affects performance  
    2. How History Scheduler performs compared to a more sophisticated one  
    3. How scheduling is affected after taking into consideration the non-uniform cost of READ/WRITE in NVM  
    4. Do all the pages need *Smart* Placement or just a fraction of them?  
    5. How the Scheduling interval affects performance? (small interval ,better performance?)  

## File Structure
### Traces
Under the folder /traces/ there are the 9 traces that were obtained using a custom pintool. 
The pintool constructed obtains information about the memory accesses that Miss the last level of Cache (which then proceed to access the main memory). The custom pintool can be found under the name mymemtrace. Intel pin needs to be installed and then the custom pintool should be made using the following command `make obj-intel64/memtrace.so` from inside the folder `source/tools/Memory/`     
Then the final benchmark outputs can be acquired after running the following command   
`path_to_pin/pin -t path_to/obj-intel64/mymemtrace.so -o <trace.out> -- <executable>`  

The Pintool output looks like this   
**Thread** , **Timestamp** , **Operation** , **Virtual Address**  

### MemProfiling
Now we want to analyze the trace-information obtained from Pin in order to retrieve the information mentioned above
Under the MemProfiling file ,the whole code is included. Every .py file has comments in the beginning describing exactly what it achieves and how it should be used.
In short the trace file is used as input for profile (which initiliazes trafficGen , scheduler and addressSpace). Then the trace file is parsed from trafficGen (through Profile class) and the addressSpace is populated. The actual *simulation* begins when the performanceModel is initiliazed taking as input Profile,Platform name, Policy ,DRAM/NVM ratio, Number of Requests Per Interval. Then the performance model is run (triggering the scheduler which was previously initiliazed to run for the given trace). After this step the PageSelector should be constructed in order to retrieve the information want.
The following code is sample of profiling the memory trace of backprop_100k
```python
trace_file ='../traces/backprop_100k'

prof = Profile(trace_file)
prof.init()

sim = PerfModel(prof, 'Fast:NearSlow', 'history', 0.2, 10000)
sim.init()
sim.run()

page_selector = PageSelector(prof, 'Fast:NearSlow', '0.2', 10000, '')
pages_misplaced = page_selector.get_misplaced_pages_sim()
```


