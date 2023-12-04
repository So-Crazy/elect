import numpy as np
import scipy as sc
import pulp as pl
class Scenario1:
    """
    最大供电能力、新能源消纳、电力支援
    """
    coup_dict1 = {'EY-EX':6,'EY-EG':7,'YZYB-MS':2,'EX-XG':-1,'EG-XG':-1}
    coup_dict2 = {'EY-EX':np.array([[3000,0,-1000,-3000,-5000,-5600],[-2500,-1500,-1000,-500,-0,500]]),
                  'EY-EG':np.array([[2300,400,-1300,-2200,-3400,-5000,-5600],[-1800,-1500,-1200,-1000,-700,-0,500]]),
                  'YZYB-MS':[[-1500,1500],[-3300,-2800]],
                  'EX-XG':3200,
                  'EG-XG':3200}
    def __init__(self,scenario,PRC,NRC,Send_inf,Rec_inf,scale,S_name,Send_Sen,Rec_Sen,S_0,S_l,S_u,Hy,Ps,If_coup,Coup_S_list1,Coup_S_list1_No,Coup_S_list2,Coup_S_list2_No,Send_HeN,Zr) -> None:
        self.scenario = scenario
        self.PRC = PRC
        self.NRC = NRC
        self.Send_inf = Send_inf#字典{'火电':,'水电':,'抽蓄':}
        self.Rec_inf = Rec_inf#字典
        self.scale = scale#出力占比
        self.S_name = S_name
        self.Send_Sen = Send_Sen
        self.Rec_Sen = Rec_Sen
        self.S_0 = S_0
        self.S_l = S_l
        self.S_u = S_u
        self.Hy = Hy
        self.Ps = Ps
        self.If_coup =If_coup
        self.Coup_S_list1 = Coup_S_list1
        self.Coup_S_list1_No = Coup_S_list1_No
        self.Coup_S_list2 = Coup_S_list2
        self.Coup_S_list2_No = Coup_S_list2_No
        self.Send_HeN = Send_HeN
        self.Zr = Zr
        self.rl()
        self.Get_a()
        self.Cal_S()
        pass
    def rl(self):
        tmp_total = sum(self.scale)
        self.RL =  self.scale/tmp_total
        pass
    def Get_a(self):
        Length = len(self.Hy)+len(self.Ps)
        Length_F = len(self.PRC)-Length
        try:
            a0 = np.zeros((Length_F,Length))
            for i in range(0,Length):
                if i<len(self.Hy):
                    a0[self.Hy[i]-1][i] = 1
                else:
                    a0[self.Ps[i-len(self.Hy)]-1][i] = 1
        
            self.a = np.hstack((np.eye(Length_F),a0))
        except:
            self.a = np.eye(Length_F)
        pass

    def Cal_S(self):
        tmp_S1 = np.hstack((self.Send_Sen,self.Rec_Sen))
        tmp_1 = -self.RL[:,np.newaxis]
        tmp_2 = np.ones((1,self.Send_Sen.shape[1]))
        Length_F = self.Send_Sen.shape[1]
            # print(Length_F)
        tmp_S2 = np.vstack((np.eye(Length_F),np.dot(tmp_1,tmp_2)))
            # print(tmp_S2[43,:])
        tmp_S = np.dot(tmp_S1,tmp_S2)
        self.cal_S2 = np.dot(tmp_S,self.a)
        pass
    
    def Solve(self):
        
        plant_num = self.a.shape[1]
        section_num = len(self.S_name)
        
        section_moment = self.S_0.tolist()
        section_upbound = self.S_u.tolist()
        section_lowbound = self.S_l.tolist()

        # plant_moments = self.plant_data[0]
        plant_upbounds = self.PRC.tolist()
        plant_lowbounds = self.NRC.tolist()

        support_sensitivity = self.cal_S2.tolist()

        Z = [self.S_name[i] for i in range(0,section_num)]
        if self.scenario == 1:
            Scenario_Solve = pl.LpProblem('最大供电能力场景MPC',sense=pl.LpMaximize)
        else:
            Scenario_Solve = pl.LpProblem('新能源消纳场景MPC',sense=pl.LpMinimize)

        # 定义片区功率调整量
        Var_delta_P = [pl.LpVariable('P'+str(i),lowBound = -plant_lowbounds[i],upBound= plant_upbounds[i],cat=pl.LpContinuous) for i in range(0,plant_num)]


        # 定义目标函数

        Object_func = pl.lpSum(Var_delta_P)

        # 定义约束条件
        Sentivity = {Z[i]:support_sensitivity[i] for i in range(0,section_num)}
        Con1 = {Z[i]+'上裕度':section_upbound[i]-section_moment[i] for i in range(0,section_num)}
        Con2 = {Z[i]+'下裕度':section_lowbound[i]-section_moment[i] for i in range(0,section_num)}
        Con3 = np.ones((1,plant_num)).tolist()
        # 添加目标函数
        Scenario_Solve += Object_func
        # 添加断面限额约束
        for i in range(0,section_num):
            Scenario_Solve += (pl.lpSum([Sentivity[Z[i]][j]*Var_delta_P[j] for j in range(0,plant_num)])<=Con1[Z[i]+'上裕度']) 
            # Scenario_Solve += (pl.lpDot(Sentivity['断面'+str(i)],Var_Z)<=Con1['断面'+str(i)])
        for i in range(0,section_num):
            Scenario_Solve += (pl.lpSum([Sentivity[Z[i]][j]*Var_delta_P[j] for j in range(0,plant_num)])>=Con2[Z[i]+'下裕度']) 
            # Scenario_Solve += (pl.lpDot(Sentivity['断面'+str(i)],Var_Z)>=Con2['断面'+str(i)])

        # 定义辅助二进制变量,添加第一类断面耦合约束
        if self.If_coup == 1:
                Length1 = self.Coup_S_list1.shape[1]
                if Length1 >0:
                    Var_bivar =  [pl.LpVariable('y'+str(i),cat=pl.LpBinary) for i in range(0,Length1)]
                    total_1 = 0;
                    for jj in range(0,Length1):
                        # total_1 = total_1+1
                        if '豫中-豫北' not in Z[self.Coup_S_list1_No[0,jj]]:
                            Scenario_Solve += self.Coup_S_list1[0,jj]-(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-1000000+1000000*Var_bivar[jj]<=0
                            Scenario_Solve += self.Coup_S_list1[0,jj]-(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-0.01+1000000*Var_bivar[jj]>=0
                            Scenario_Solve += self.Coup_S_list1[1,jj]-(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[1,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-1000000+1000000*Var_bivar[jj]<=0
                        elif '豫中-豫北' not in Z[self.Coup_S_list1_No[0,jj-1]]:
                            Scenario_Solve += self.Coup_S_list1[0,jj]-(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-1000000+1000000*Var_bivar[jj]<=0
                            Scenario_Solve += self.Coup_S_list1[0,jj]-(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-0.01+1000000*Var_bivar[jj]>=0
                            Scenario_Solve += self.Coup_S_list1[1,jj]+(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[1,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-1000000+1000000*Var_bivar[jj]<=0
                        else:
                            Scenario_Solve += self.Coup_S_list1[0,jj]+(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-1000000+1000000*Var_bivar[jj]<=0
                            Scenario_Solve += self.Coup_S_list1[0,jj]-(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-0.01+1000000*Var_bivar[jj]>=0
                            Scenario_Solve += self.Coup_S_list1[1,jj]+(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list1_No[1,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))-1000000+1000000*Var_bivar[jj]<=0
                        if (jj<14):
                            if (Z[self.Coup_S_list1_No[1,jj]] != Z[self.Coup_S_list1_No[1,jj+1]])  :
                                Scenario_Solve += pl.lpSum([Var_bivar[i] for i in range(total_1,jj+1)])>=1
                                total_1 =  jj+1
                        else:
                            Scenario_Solve += pl.lpSum([Var_bivar[i] for i in range(total_1,jj+1)])>=1
                            total_1 = total_1 + jj+1

                Length2 = self.Coup_S_list2.shape[1]
                for jj in range(0,Length2):
                    print(-1+self.Coup_S_list2_No[0,jj],-1+self.Coup_S_list2_No[1,jj])
                    Scenario_Solve += self.Coup_S_list2[0,jj]*section_moment[-1+self.Coup_S_list2_No[0,jj]]+self.Coup_S_list2[1,jj]*section_moment[-1+self.Coup_S_list2_No[1,jj]] +\
                    self.Coup_S_list2[0,jj]*(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list2_No[0,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))+\
                    self.Coup_S_list2[1,jj]*(pl.lpSum([Sentivity[Z[-1+self.Coup_S_list2_No[1,jj]]][j]*Var_delta_P[j] for j in range(0,plant_num)]))<=3200     

        # 备用容量约束
        if self.Send_HeN == 1:# 只包括河南全部片区
            tmp_a = np.dot(np.ones((1,plant_num-len(self.Hy)-len(self.Ps))),self.a)
            Scenario_Solve += (pl.lpSum([tmp_a[0,j]*(self.PRC[j]-Var_delta_P[j]) for j in range(0,plant_num)]))>=self.Zr[1]+0.2*self.Zr[2]     
        elif self.Send_HeN  == 2:# 全网片区
            tmp_a = np.dot(np.ones((1,plant_num-len(self.Hy)-len(self.Ps))),self.a)
            Scenario_Solve += (pl.lpSum([tmp_a[0,j]*(self.PRC[j]-Var_delta_P[j]) for j in range(0,19)]))>=self.Zr[1]+0*self.Zr[2]
            Scenario_Solve += (pl.lpSum([(self.PRC[j]-Var_delta_P[j]) for j in range(0,plant_num)]))>=self.Zr[1]+0.2*self.Zr[2]
        elif self.Send_HeN == 3:# 不包括河南省网的情况
            Scenario_Solve += (pl.lpSum([(self.PRC[j]-Var_delta_P[j]) for j in range(0,plant_num)]))>=0*self.Zr[1]+0.2*self.Zr[2]

        Scenario_Solve.writeLP('测试')
        print(pl.listSolvers(onlyAvailable=True))
        # 开始求解
        Scenario_Solve.solve(solver=pl.get_solver('PULP_CBC_CMD'))
        print(pl.LpStatus[Scenario_Solve.status])
        res_Z = [pl.value(i) for i in Var_delta_P]
        section_later = np.dot(support_sensitivity,np.array(res_Z))+self.S_0

        best = [res_Z,section_later-self.S_0,section_later,pl.value(Scenario_Solve.objective)]
        #       self.gbest:片区功率调整量   np.dot(aeq,res.x):负荷调减量  section_later:调整后断面功率   adjust_total:断面功率变化量 
        return best
        
        
        pass
