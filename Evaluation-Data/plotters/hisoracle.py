import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import random 

df = pd.read_csv (r'../data/History_Oracle',header=None)
df.columns = ['benchmark','policy','ratio','periods','total','hitrate']
ratio=1/8

#print(df.head(5))

fig, ax = plt.subplots(figsize=(12,7))
width = 0.2
x= np.arange(1)
j=0.2
benchmarks = ['backprop_100k','streamcluster','hotspot_1024','lud_2048','blackscholes','bodytrack','bplustree','kmeans_80k']
#benchmarks = ['blackscholes','kmeans_80k','backprop_100k','streamcluster','hotspot_1024','lud_2048','bodytrack','bplustree']


#boost = [0.06,0.04,0.13,-0.06,0.08,0.01,0.05,0.1]
tick=[]

benchmarkslabels= ['blackscholes','kmeans','backprop','streamcluster','hotspot','lud','bodytrack','bplustree']
i=0.2

for bm in benchmarks:
    newD = df[df['benchmark']==bm]
    newD = newD[newD['ratio']==1/16]
    #print(bm)
    #print(newD)
    newDhis = newD[newD['policy']==' history']
    newDOracle = newD[newD['policy']==' oracle']
    hitrateHis = float(newDhis['hitrate']/newDhis['total'])
    hitrateOracle= float(newDOracle['hitrate']/newDOracle['total'])
    print(bm,hitrateHis,hitrateOracle)
    
    
    if j==0.2:
        plt.bar(x+j, hitrateHis*100,label='history',color='darkslateblue',width=width)
        plt.bar(x+j+i,hitrateOracle*100,label='oracle',color='dimgray',width=width)
    else:
        plt.bar(x+j, hitrateHis*100,color='darkslateblue',width=width)
        plt.bar(x+j+i,hitrateOracle*100,color='dimgray',width=width)
    tick.append(j+width/2)
    j+=1


plt.ylabel('DRAM Hit-rate',fontsize=12)
ax.grid(True,color='gray',linestyle='--', which='major')

plt.ylim([0, 100])
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=True)
plt.legend(bbox_to_anchor=(1.14, 1),ncol=1,fontsize=12)
# bbox_to_anchor=(0,0.92,1.01,0.15)
plt.title(label='History-Oracle Performance Gap')
#fig.text(.5, .05, txt, ha='center')
plt.xticks(tick, list(benchmarkslabels), fontsize=10)
plt.savefig("plots/HistoryOracle.pdf")   
plt.savefig("plots/HistoryOracle.png")   
plt.show()
