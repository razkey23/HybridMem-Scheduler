import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import random 

#df = pd.read_csv (r'../data/TempEval_v3',header=None)
df = pd.read_csv (r'../data/EvalData',header=None)
df.columns = ['benchmark','policy','hitrate','writehitrate','readhitrate','totalreads','totalwrites']

fig, ax = plt.subplots(figsize=(10,7))
width = 0.2
x= np.arange(1)
j=0.2


benchmarks = ['backprop_100k','streamcluster','hotspot_1024','lud_2048','blackscholes','bodytrack','bplustree','kmeans_80k']
benchmarkslabels= ['backprop','streamcluster','hotspot','lud','blackscholes','bodytrack','bplustree','kmeans']
#benchmarks = ['backprop_100k','streamcluster','hotspot_1024','lud_2048','blackscholes','bodytrack','bplustree']
policies=[' History',' Oracle',' Hybrid',' PHybrid',' PEVHybrid']

boost = [0.25,0.0815,0.05,0.29,0.172,0.085,0.235,0.052]

tick=[]
i=0.3
for bm in benchmarks:
    newD = df[df['benchmark']==bm]
    
    minV = int(newD[newD['policy']==' History']['hitrate'])
    
    maxV = int(newD[newD['policy']==' Hybrid']['hitrate'])
    
    

    phybrid = int(newD[newD['policy']==' PHybrid']['hitrate'])
    #temp = int(newD[newD['policy']==' kleio']['hitrate'])
    #print(newD[newD['policy']==' kleio']['hitrate'])
    kleio = int(newD[newD['policy']==' kleio']['hitrate'])
    

    pevnormalized = (phybrid-minV)/(maxV-minV)
    #normalized = pevnormalized-boost[int(j)]
    normalized = (kleio-minV)/(maxV-minV)

    if j==0.2:
        plt.bar(x+j, normalized*100,label='kleio',color='#c7e9b4',width=width+0.1)
        plt.bar(x+j+i,pevnormalized*100,label='9-N RNN',color='#253494',width=width+0.1)
        #plt.bar(x+j+2*i,temp*100,label='9-N RNN',color='red',width=width)
    else:
        plt.bar(x+j, normalized*100,color='#c7e9b4',width=width+0.1)
        plt.bar(x+j+i,pevnormalized*100,color='#253494',width=width+0.1)
        #plt.bar(x+j+2*i,temp*100,label='9-N RNN',color='red',width=width)
    tick.append(j+width/2)
    j+=1

plt.ylabel('DRAM Hitrate',fontsize=12)
ax.grid(True,color='lightgray',linestyle='--', which='major')

plt.ylim([0, 100])
#ax.yaxis.grid(True,color='gray',linestyle='-', which='major')
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=True)
plt.title(label='Hitrate Improvement via Machine-Learning')
plt.legend()
#fig.text(.5, .05, txt, ha='center')
plt.xticks(tick, list(benchmarkslabels), fontsize=10)
plt.savefig("EvaluationPlots/DRAMHitrate_MineVsKleio.pdf")   
plt.savefig("EvaluationPlots/DRAMHitrate_MineVsKleio.png")  
#plt.show()