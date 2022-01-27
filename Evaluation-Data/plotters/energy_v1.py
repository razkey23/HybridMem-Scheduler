import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import random 

df = pd.read_csv (r'../data/Energy_v2',header=None)
df.columns = ['benchmark','numpages','dramReads','dramWrites','history','oracle','hybrid']


df1 = pd.read_csv (r'../data/EvalData',header=None)
df1.columns = ['benchmark','policy','hitrate','writehitrate','readhitrate','totalreads','totalwrites']
benchmarks = ['backprop_100k','streamcluster','hotspot_1024','lud_2048','blackscholes','bodytrack','bplustree','kmeans_80k']

df2 = pd.read_csv (r'../data/Energy_v3',header=None)
df2.columns = ['benchmark','policy','hitrate','writehitrate','readhitrate','totalreads','migrations','totalwrites']


nvmRead = 80.41 #nJ
nvmWrite = 418.6 #nJ
dramRead = 5.9 #nJ
dramWrite = 12.7 #nJ
nanotomili=10**6 #convert nano to milli
policies = [' NoManage',' Kleio',' Hybrid',' Oracle',' History']

policies = [' NoManage',' History',' Kleio',' Hybrid']

#df2 = pd.read_csv (r'../data/Energy_eval',header=None)
df1 = pd.read_csv(r'../data/Energy_eval',header=None)
df1.columns = ['benchmark','policy','dramReads','dramWrites','totalReads','totalWrites','migrations']

print(df1.head(10))


#Get totalPages = memfootprint
idlePower={} # T is missing
for bm in benchmarks:
    #idle = 451*10**(-6) #mW/GB to mW/GB , switch to mW/KB 
    #remove 10**(-6) see 1.
    idle = 451
    newDf=df[df['benchmark']==bm]
    # DRAM memfootprint in KB
    memfootprint = 4*(1/8)*newDf['numpages'].iloc[0] #4 ΚΒ * 1/8 dram:nvm ratio
    #1. memfootprint in KB , idle in mW/KB , result in mW , multiply by 10**6 (to get nW)
    idlePower[bm] = memfootprint*idle #result is in nJ  10=seconds runtime 
    idlePower[bm] /= nanotomili #result now in MilliJ



nvmCons = []
nvmDramCons = []
nvmDramMigration = []
nvmDramMigrationIdle = []
benchm=[]
polc=[]

benchmarkslabels= ['backprop','streamcluster','hotspot','lud','blackscholes','bodytrack','bplustree','kmeans']


for bm in benchmarks:
    baseline=1
    
    hisDramReads=0
    hisDramWrites=0
    hisMigrations=0
    nMDramReads=0
    nMDramWrites=0
    nMMigrations=0

    for pol in policies:
        newDf=df1[df1['benchmark']==bm]
        newDf = newDf[newDf['policy']==pol]
        totalReads = float(newDf['totalReads'].iloc[0])
        totalWrites = float(newDf['totalWrites'].iloc[0])
        dramReads = float(newDf['dramReads'].iloc[0])
        dramWrites = float(newDf['dramWrites'].iloc[0])

        
        # Calculate Migration Cost 
        if pol==' NoManage':
            halfmigrations=0
            totalReads = float(newDf['totalReads'].iloc[0])
        else :
            halfmigrations = float(newDf['migrations'].iloc[0])/2
                
        
        migrationCost = halfmigrations * (nvmRead+dramWrite+nvmWrite+dramRead) #in nJ convert to mili
        migrationCost /= nanotomili




        # DRAM consumption in mJ
        dramConsumption = dramReads*dramRead + dramWrites * dramWrite
        dramConsumption /= nanotomili

        # NVM consumption in mJ
        nvmConsumption = (totalReads-dramReads)*nvmRead + (totalWrites-dramWrites) * nvmWrite
        nvmConsumption /= nanotomili
        
        #Calculate Idle Power properly in mJ * multiply by runtime
        readsEstimatedLatency = dramReads * (8) + (totalReads-dramReads) * (24) #ns
        writesEstimatedLatency = dramWrites * (50) + (totalWrites-dramWrites)*1000  #ns
        totalLatency = (readsEstimatedLatency+writesEstimatedLatency)/nanotomili #ms
        totalLatency /= 10
        print(totalLatency)
        idleEnergy = idlePower[bm]*totalLatency
        
        #TotalCost
        totalEn = nvmConsumption+dramConsumption + idleEnergy+migrationCost
        
        if pol == ' NoManage':
            baseline=totalEn
            
        
    
        
        #stackedPlot
        benchm.append(bm)
        polc.append(pol)

        newB = totalEn/baseline
        #nvmCons.append(nvmConsumption/baseline)
        nvmCons.append(newB*(nvmConsumption/totalEn))
        print(bm,pol,dramConsumption,idleEnergy,nvmConsumption)
        #nvmDramCons.append( nvmConsumption/baseline+dramConsumption/baseline)
        nvmDramCons.append(newB*(dramConsumption/totalEn))
        nvmDramMigration.append(newB*(migrationCost/totalEn))
        nvmDramMigrationIdle.append(newB*(idleEnergy/totalEn))   

        


bar_width = 0.3
df=pd.DataFrame({'benchmark':benchm,'policy':polc,'Idle Power':nvmDramMigrationIdle, 'Migration':nvmDramMigration, 'DRAM':nvmDramCons,'NVM':nvmCons})




#1st PLOT Migration-IdlePower-NVM-DRAM Consumption info


fig, ax = plt.subplots()
index = np.linspace(0,1.5,4)
mids=[]

for bm in benchmarks:
    #for pol in policies:
    newDf=df[df['benchmark']==bm]

    ab_bar_list = [plt.bar(index[::-1],newDf['NVM'],color='blue', width= 0.2),
               plt.bar(index[::-1], newDf['DRAM'],bottom=newDf['NVM'],color='yellow', width= 0.2),
               plt.bar(index[::-1], newDf['Idle Power'],bottom=newDf['NVM']+newDf['DRAM']+newDf['Migration'],color='red', width= 0.2),
               plt.bar(index[::-1], newDf['Migration'],bottom=newDf['NVM']+newDf['DRAM'],color='green', width= 0.2)]
    mids.append(index[0]+(index[3]-index[0])/2)

    for i in range(len(policies)):
        labelPos = newDf['NVM'].iloc[i] +  newDf['Migration'].iloc[i] +newDf['DRAM'].iloc[i] + newDf['Idle Power'].iloc[i]
        #plt.annotate(policies[i],xy=(index[i],labelPos),ha='center',va='bottom')
    
    index+=3

legendLabels=['NVM Consumption','DRAM Consumption','Idle Power','Page Migration']
plt.legend(legendLabels,bbox_to_anchor=(0,0.88,1,0.2),loc='upper left',mode='expand',ncol=4,fontsize=6)
ax.set_xticklabels(benchmarkslabels,fontsize=6)
ax.set_xticks(mids)
ax.set_ylabel('Normalized Energy Consumption',fontsize=8)
ax.set_ylim(0,1.1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
#plt.show()
#plt.savefig("EvaluationPlots/pdfs/EnergyConsumptionDetails.pdf")   
#plt.savefig("EvaluationPlots/pngs/EnergyConsumptionDetails.png")  



'''

#2ND PLOT ONLY Policy info

fig, ax = plt.subplots()
#fig = plt.figure(figsize=(20,10))


#index=[i for i in range(0,1,0.2)]
index = np.linspace(0,1.5,4)
mids=[]

#print(list(index)

colors = ['red','blue','green','darkorange']
hatches =['xxxx','//','///////','']

#Reverse Everything
polRev=policies[::-1]
colors = colors[::-1]
hatches = hatches[::-1]

for bm in benchmarks:
    #for pol in policies:
    newDf=df[df['benchmark']==bm]


    print(newDf)
    l=len(polRev)-1
    for i in range(len(polRev)):
        labelPos = newDf['NVM'].iloc[l-i] +  newDf['Migration'].iloc[l-i] +newDf['DRAM'].iloc[l-i] + newDf['Idle Power'].iloc[l-i]
        bar = plt.bar(index[i],labelPos,hatch=hatches[i],color=colors[i],width= 0.25)
        #plt.annotate(policies[i],xy=(index[i],labelPos),ha='center',va='bottom')
    
    
    
    mids.append(index[0]+(index[3]-index[0])/2)

    #Labeling the policies
    
    index+=3

legendLabels=['NoManage','History','Kleio','9-RNN']
legendLabels=legendLabels[::-1]
plt.legend(legendLabels,bbox_to_anchor=(0,0.88,1,0.2),loc='upper left',mode='expand',ncol=4,fontsize=6)
#plt.grid()
#ax.grid(True,color='gray',linestyle='--', which='major')
ax.set_ylim(0,1.1)
ax.set_ylabel('Normalized Energy Consumption',fontsize=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticklabels(benchmarkslabels,fontsize=6)
ax.set_xticks(mids)

plt.savefig("EvaluationPlots/pdfs/CompEnergyConsumption.pdf")   
plt.savefig("EvaluationPlots/pngs/CompEnergyConsumption.png")  
#plt.show()

'''