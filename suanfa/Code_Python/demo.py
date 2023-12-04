import pandas as pd
import numpy as np
from GetScenario1 import Scenario1 as Sc1
from GetScenario2 import Scenario2 as Sc2
from GetScenario3 import Scenario3 as Sc3
from GetScenario4 import Scenario4 as Sc4
import os as o

path = r'D:\_学习数据\华中电网\_科技项目代码\备用计算数据20231008备份\20230824数据\备用数据0824\湖北湖南数据0824.xls'
path2 = r'D:\_学习数据\华中电网\_科技项目代码\备用计算数据20231008备份\20230824数据\备用数据0824\灵敏度20231013.xlsx'
path3 = r'D:\_学习数据\华中电网\_科技项目代码\备用计算数据20231008备份\20230824数据\备用数据0824\数据整理'
Data = pd.read_excel(path,sheet_name='Sheet2')
S_0 = pd.read_excel(path2,sheet_name='Sheet1').to_numpy()
S_name = pd.read_excel(path2,sheet_name='Sheet1').iloc[0,5:20].index.tolist()

S_0 = S_0[0:42,5:20].T

Duanmian_Data = o.listdir(path3)

S0 = []
Sl = []
Su = []
for i in S_name:
    tmp_flag = 0
    for j in Duanmian_Data:
        if i in j:
            tmp_data = pd.read_excel(path3+'\\'+j).to_numpy()
            S0.append(tmp_data[:96,-3].tolist())
            Sl.append(tmp_data[:96,-1].tolist())
            Su.append(tmp_data[:96,-2].tolist())
            tmp_flag = 1
    if tmp_flag == 0:
        print(i)
S0 = np.array(S0)
Sl = np.array(Sl)
Su = np.array(Su)
# S_dataframe = pd.DataFrame(S0)
# pd.to_excel(S_dataframe,)


# Hy = [6,13,20,21,24,28,29,31,32,34,35,36,38,39,41,42]
Hy = [6,13,20,21,24,28,29,31,32,34,35,36,38,39,41,42]
Ps = [9,14,23,33,35,36]


print(Duanmian_Data[0][2:4])
Data_pianqu = Data.to_numpy()
PRC_Hy = []
NRC_Hy = []

for i in Hy:
    tmp_Hy_P = Data_pianqu[:,15].reshape([96,42])
    PRC_Hy.append(tmp_Hy_P.T[i-1,:])
    tmp_Hy_N = Data_pianqu[:,19].reshape([96,42])
    NRC_Hy.append(tmp_Hy_N.T[i-1,:])

PRC_Hy = np.array(PRC_Hy)    
NRC_Hy = np.array(NRC_Hy)    

PRC_Ps = []
NRC_Ps = []

for i in Ps:
    tmp_Ps_P = Data_pianqu[:,16].reshape([96,42])
    PRC_Ps.append(tmp_Ps_P.T[i-1,:])
    tmp_Ps_N = Data_pianqu[:,20].reshape([96,42])
    NRC_Ps.append(tmp_Ps_N.T[i-1,:])

PRC_Ps = np.array(PRC_Ps)    
NRC_Ps = np.array(NRC_Ps)   


PRC_F = Data_pianqu[:,14]
PRC_F=PRC_F.reshape([96,42])
NRC_F = Data_pianqu[:,18]
NRC_F=NRC_F.reshape([96,42])

PRC_F = PRC_F.T
NRC_F = NRC_F.T

PRC1 = np.hstack((PRC_F[0:42,0],PRC_Hy[:,0],PRC_Ps[:,0]))
NRC1 = np.hstack((NRC_F[0:42,0],NRC_Hy[:,0],NRC_Ps[:,0]))

load = np.abs(Data_pianqu[0:42,12])
Send_Sen = S_0[:,0:42]
Rec_Sen = S_0[:,0:42]


# 1最大供电能力场景
MPC = Sc1(
        scenario=1,
        PRC= PRC1.T,
        NRC= NRC1.T,
        Send_inf=np.linspace(1,42,42),
        Rec_inf=np.linspace(1,42,42),
        scale=load,
        S_name=S_name,
        Send_Sen=Send_Sen,
        Rec_Sen=Rec_Sen,
        S_0=S0[:,0],
        S_l=Sl[:,0],
        S_u=Su[:,0],
        Hy=(np.array(Hy)-0).tolist(),
        Ps=(np.array(Ps)-0).tolist(),
        If_coup=0,
        Coup_S_list1=np.array([[3000,0,-1000,-3000,-5000,-5600,2300,400,-1300,-2200,-3400,-5000,-5600,-1500,1500],[-2500,-1500,-1000,-500,-0,500,-1800,-1500,-1200,-1000,-700,-0,500,-3300,-2800]]),
        Coup_S_list1_No=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,11,11],[2,2,2,2,2,2,3,3,3,3,3,3,3,12,12]]),
        Coup_S_list2=np.array([[-1,-1],[1,-1]]),
        Coup_S_list2_No=np.array([[2,3],[4,4]]),
        Send_HeN=2,
        Zr = [0,0,sum(load)]
        )
Res1 = MPC.Solve()
# print(Res1[3],sum(PRC1))

# 2新能源消纳场景

PRC1 = np.hstack((PRC_F[0:42,0],PRC_Hy[:,0],PRC_Ps[:,0]))
NRC1 = np.hstack((NRC_F[0:42,0],NRC_Hy[:,0],NRC_Ps[:,0]))

load1 = np.abs(Data_pianqu[0:42,7])+np.abs(Data_pianqu[0:42,8])
Send_Sen = -S_0[:,0:42]
Rec_Sen = -S_0[:,0:42]
MPC2 = Sc1(
        scenario=2,
        PRC= PRC1.T,
        NRC= NRC1.T,
        Send_inf=np.linspace(1,42,42),
        Rec_inf=np.linspace(1,42,42),
        scale=load1,
        S_name=S_name,
        Send_Sen=Send_Sen,
        Rec_Sen=Rec_Sen,
        S_0=S0[:,0],
        S_l=Sl[:,0],
        S_u=Su[:,0],
        Hy=(np.array(Hy)-0).tolist(),
        Ps=(np.array(Ps)-0).tolist(),
        If_coup=0,
        Coup_S_list1=np.array([[3000,0,-1000,-3000,-5000,-5600,2300,400,-1300,-2200,-3400,-5000,-5600,-1500,1500],[-2500,-1500,-1000,-500,-0,500,-1800,-1500,-1200,-1000,-700,-0,500,-3300,-2800]]),
        Coup_S_list1_No=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,11,11],[2,2,2,2,2,2,3,3,3,3,3,3,3,12,12]]),
        Coup_S_list2=np.array([[-1,-1],[1,-1]]),
        Coup_S_list2_No=np.array([[2,3],[4,4]]),
        Send_HeN=2,
        Zr = [0,0,sum(load)]
        )
Res_rea = MPC2.Solve()
print(Res_rea[3],sum(NRC1))

# 3水电消纳
PRC1 = np.hstack((PRC_Hy[:,0],PRC_F[0:42,0]))
NRC1 = np.hstack((NRC_Hy[:,0],NRC_F[0:42,0]))

Send_Sen = S_0[:,(np.array(Hy[:])-1).tolist()]
Rec_Sen = S_0[:,0:42]
HA = Sc2(
        PRC= PRC1.T,
        NRC= NRC1.T,
        Send_inf=Hy[:],
        Rec_inf=np.linspace(1,42,42),
        scale=1,
        S_name=S_name,
        Send_Sen=Send_Sen,
        Rec_Sen=Rec_Sen,
        S_0=S0[:,0],
        S_l=Sl[:,0],
        S_u=Su[:,0],
        Hy=[],
        Ps=[],
        If_coup=0,
        Coup_S_list1=np.array([[3000,0,-1000,-3000,-5000,-5600,2300,400,-1300,-2200,-3400,-5000,-5600,-1500,1500],[-2500,-1500,-1000,-500,-0,500,-1800,-1500,-1200,-1000,-700,-0,500,-3300,-2800]]),
        Coup_S_list1_No=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,11,11],[2,2,2,2,2,2,3,3,3,3,3,3,3,12,12]]),
        Coup_S_list2=np.array([[-1,-1],[1,-1]]),
        Coup_S_list2_No=np.array([[2,3],[4,4]]),
        Send_HeN=2,
        Zr = [0,0,sum(load)]
        )
Res2 = HA.Solve()
print(Res2[3],sum(PRC1[0:16]))

# 4直流消纳
PRC1 = np.hstack((np.array([12000-6000]),PRC_F[0:42,0],PRC_Hy[:,0],PRC_Ps[:,0]))
NRC1 = np.hstack((np.array([0]),NRC_F[0:42,0],NRC_Hy[:,0],NRC_Ps[:,0]))

Send_Sen = S_0[:,1][:,np.newaxis]
Rec_Sen = np.hstack((S_0[:,0:42],S_0[:,(np.array(Hy)-1).tolist()],S_0[:,(np.array(Ps)-1).tolist()]))
DCA = Sc2(
        PRC= PRC1.T,
        NRC= NRC1.T,
        Send_inf=[2],
        Rec_inf=np.linspace(1,42,42),
        scale=1,
        S_name=S_name,
        Send_Sen=Send_Sen,
        Rec_Sen=Rec_Sen,
        S_0=S0[:,0],
        S_l=Sl[:,0],
        S_u=Su[:,0],
        Hy=[],
        Ps=[],
        If_coup=0,
        Coup_S_list1=np.array([[3000,0,-1000,-3000,-5000,-5600,2300,400,-1300,-2200,-3400,-5000,-5600,-1500,1500],[-2500,-1500,-1000,-500,-0,500,-1800,-1500,-1200,-1000,-700,-0,500,-3300,-2800]]),
        Coup_S_list1_No=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,11,11],[2,2,2,2,2,2,3,3,3,3,3,3,3,12,12]]),
        Coup_S_list2=np.array([[-1,-1],[1,-1]]),
        Coup_S_list2_No=np.array([[2,3],[4,4]]),
        Send_HeN=2,
        Zr = [0,0,sum(load)]
        )
Res_DCA = DCA.Solve()
print(Res_DCA[3],sum(PRC1[1:65]))


# 5跨区转送
PRC1 = np.hstack(PRC_F[0:42,0])
NRC1 = np.hstack(NRC_F[0:42,0])
PRC1[1] = 2000
# PRC1[18] = 6000-1063
PRC1[28] = 0
NRC1[1] = 0
# NRC1[18] = 0
NRC1[28] = 6000
Send_Sen = S_0[:,0:42]
Rec_Sen = []
ZhuanSong = Sc3(
        PRC= PRC1.T,
        NRC= NRC1.T,
        Send_inf=[2],
        Rec_inf=[29],
        scale=1,
        S_name=S_name,
        Send_Sen=Send_Sen,
        Rec_Sen=Rec_Sen,
        S_0=S0[:,0],
        S_l=Sl[:,0],
        S_u=Su[:,0],
        Hy=[],
        Ps=[],
        If_coup=1,
        Coup_S_list1=np.array([[3000,0,-1000,-3000,-5000,-5600,2300,400,-1300,-2200,-3400,-5000,-5600,-1500,1500],[-2500,-1500,-1000,-500,-0,500,-1800,-1500,-1200,-1000,-700,-0,500,-3300,-2800]]),
        Coup_S_list1_No=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,11,11],[2,2,2,2,2,2,3,3,3,3,3,3,3,12,12]]),
        Coup_S_list2=np.array([[-1,-1],[1,-1]]),
        Coup_S_list2_No=np.array([[2,3],[4,4]]),
        Send_HeN=2,
        Zr = [0,0,sum(load)]
        )
Res_ZhuanSong = ZhuanSong.Solve()
print(Res_ZhuanSong[3],sum(PRC1[0:42]))


# 6应急功率支援能力
PRC1 = np.vstack((PRC_F[0:42,0],(Data_pianqu[0:42,14]+Data_pianqu[0:42,4])*1.5*5/100))
NRC1 = np.vstack((NRC_F[0:42,0],(Data_pianqu[0:42,14]+Data_pianqu[0:42,4])*1.5*5/100))

PRC1 = np.min(PRC1,0)
NRC1 = np.max(NRC1,0)

PRC1 = np.hstack((PRC1,PRC_Hy[:,0],PRC_Ps[:,0]))
NRC1 = np.hstack((NRC1,NRC_Hy[:,0],NRC_Ps[:,0]))

S0_ = -0.5*(S_0[:,1]+S_0[:,2])*3000+S0[:,0]
Send_Sen = np.hstack((S_0[:,0:42],S_0[:,(np.array(Hy)-1).tolist()],S_0[:,(np.array(Ps)-1).tolist()]))


load = np.abs(Data_pianqu[0:42,12])
YJGL = Sc4(
        PRC= PRC1.T,
        NRC= NRC1.T,
        Send_inf=[],
        Rec_inf=[],
        scale=1,
        S_name=S_name,
        Send_Sen=Send_Sen,
        Rec_Sen=[],
        S_0=S0_,
        S_l=Sl[:,0],
        S_u=Su[:,0],
        Hy=[],
        Ps=[],
        If_coup=1,
        Coup_S_list1=np.array([[3000,0,-1000,-3000,-5000,-5600,2300,400,-1300,-2200,-3400,-5000,-5600,-1500,1500],[-2500,-1500,-1000,-500,-0,500,-1800,-1500,-1200,-1000,-700,-0,500,-3300,-2800]]),
        Coup_S_list1_No=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,11,11],[2,2,2,2,2,2,3,3,3,3,3,3,3,12,12]]),
        Coup_S_list2=np.array([[-1,-1],[1,-1]]),
        Coup_S_list2_No=np.array([[2,3],[4,4]]),
        Send_HeN=2,
        Zr = [0,0,sum(load)*0.5]
        )
Res_YJGL = YJGL.Solve()
print(Res_YJGL[3]-3000,sum(PRC1))

print('a')