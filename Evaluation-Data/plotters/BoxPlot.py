import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv (r'../data/BoxPlot_new',header=None)
df.columns = ['benchmark','pageid','his_rmse','rnn1_rmse','rnn_rmse']

#print(df.head(10))
benchmarks = ['backprop_100k','streamcluster','hotspot_1024','lud_2048','blackscholes','bodytrack','bplustree','kmeans_80k']
benchmarkslabels= ['backprop','streamcluster','hotspot','lud','blackscholes','bodytrack','bplustree','kmeans']
#benchmarks = ['backprop_100k','streamcluster','hotspot_1024','blackscholes','bodytrack','bplustree','kmeans_80k']
#benchmarkslabels= ['backprop','streamcluster','hotspot','blackscholes','bodytrack','bplustree','kmeans']

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color='#f1a340')
    ##f1a340

fig, ax = plt.subplots(figsize=(14,8))
#plt.figure()


data=[[] for i in range(len(benchmarks))]
dataHis=[]
dataRnn=[]
dataRnn1=[]
for bm in benchmarks:
    newDf=df[df['benchmark']==bm]
    arrayHis = np.array(newDf['his_rmse'])
    arrayRnn = np.array(newDf['rnn_rmse'])
    arrayRnn1 = np.array(newDf['rnn1_rmse'])
    dataHis.append(arrayHis)
    dataRnn.append(arrayRnn)
    dataRnn1.append(arrayRnn1)
#pd.options.display.mpl_style = 'default'


bpl = plt.boxplot(dataHis,whis=0,showfliers=False, positions=np.array(range(len(dataHis)))-0.18, sym='', widths=0.15)
bp =  plt.boxplot(dataRnn1,whis=0, showfliers=False,positions=np.array(range(len(dataRnn))), sym='', widths=0.15)
bpr = plt.boxplot(dataRnn, whis=0,showfliers=False,positions=np.array(range(len(dataRnn)))+0.18, sym='', widths=0.15)
#print(np.array(range(len(dataRnn)))*1.5+0.2)
set_box_color(bpl, '#67001f') # colors are from http://colorbrewer2.org/
set_box_color(bp, '#df65b0')
set_box_color(bpr, '#225ea8')
plt.grid(True,color='lightgray',linestyle='-')


plt.plot([], c='#67001f', label='History')
plt.plot([], c='#df65b0', label='kleio')
plt.plot([], c='#225ea8', label='9-N RNN')

plt.legend(prop={'size': 10})
ticks = benchmarkslabels
plt.xticks(range(0, len(ticks) *1,1), ticks,fontsize=12)
print(range(0, len(ticks) * 2, 2))
plt.ylabel('Root Mean Square Error',fontsize=16)

#plt.xlim(-2, len(ticks)*2)
#plt.ylim(0, 8)
#plt.tight_layout()
plt.savefig("EvaluationPlots/BoxPlot_MultipleEval.pdf")
plt.savefig("EvaluationPlots/BoxPlot_MultipleEval.png")
plt.show()

