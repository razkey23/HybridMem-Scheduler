import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import random 

df = pd.read_csv (r'../data/EvalData',header=None)
df.columns = ['benchmark','policy','hitrate','readhitrate','writehitrate','totalreads','totalwrites']

fig, ax = plt.subplots(figsize=(10,7))
width = 0.2
x= np.arange(1)
j=0.2
#benchmarks = ['backprop_100k','streamcluster','hotspot_1024','lud_2048','blackscholes','bodytrack','bplustree','kmeans_80k']
benchmarks = ['blackscholes','kmeans_80k','backprop_100k','streamcluster','hotspot_1024','lud_2048','bodytrack','bplustree']
policies=[' History',' Oracle',' Hybrid',' PHybrid',' PEVHybrid']

#boost = [0.06,0.04,0.13,-0.06,0.08,0.01,0.05,0.1]
tick=[]

benchmarkslabels= ['blackscholes','kmeans','backprop','streamcluster','hotspot','lud','bodytrack','bplustree']
i=0.2

for bm in benchmarks:
    newD = df[df['benchmark']==bm]
    minV = int(newD[newD['policy']==' History']['hitrate'])
    
    maxV = int(newD[newD['policy']==' Hybrid']['hitrate'])
    


    phybrid = int(newD[newD['policy']==' PHybrid']['hitrate'])
    pevhybrid = int(newD[newD['policy']==' PEVHybrid']['hitrate'])
    #phybrid = int(newD[newD['policy']==' PHybrid']['readhitrate'])+int(newD[newD['policy']==' PHybrid']['writehitrate'])

    normalized = (phybrid-minV)/(maxV-minV)
    pevnormalized = (pevhybrid-minV)/(maxV-minV)

    print(bm,normalized)
    if j==0.2:
        plt.bar(x+j, normalized*100,label='LRU',color='gray',width=width)
        plt.bar(x+j+i,pevnormalized*100,label='clustered LRU',color='red',width=width)
    else:
        plt.bar(x+j, normalized*100,color='gray',width=width)
        plt.bar(x+j+i,pevnormalized*100,color='red',width=width)
    tick.append(j+width/2)
    j+=1

plt.ylabel('DRAM Hit Rate',fontsize=12)
ax.grid(True,color='gray',linestyle='--', which='major')

plt.ylim([0, 100])
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=True)
plt.title(label='DRAM Hit Rate '+" %" + ' - Eviction Policy')
plt.legend()
#fig.text(.5, .05, txt, ha='center')
plt.xticks(tick, list(benchmarkslabels), fontsize=10)
plt.savefig("EvaluationPlots/DRAMHitrate_EvictionPolicy.pdf")   
plt.savefig("EvaluationPlots/DRAMHitrate_EvictionPolicy.png")   
plt.show()