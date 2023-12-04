import numpy as np
import scipy as sc
import pulp as pl
class Scenario3:
    """
    跨区转送
    """
    coup_dict1 = {'EY-EX':6,'EY-EG':7,'YZYB-MS':2,'EX-XG':-1,'EG-XG':-1}
    coup_dict2 = {'EY-EX':np.array([[3000,0,-1000,-3000,-5000,-5600],[-2500,-1500,-1000,-500,-0,500]]),
                  'EY-EG':np.array([[2300,400,-1300,-2200,-3400,-5000,-5600],[-1800,-1500,-1200,-1000,-700,-0,500]]),
                  'YZYB-MS':[[-1500,1500],[-3300,-2800]],
                  'EX-XG':3200,
                  'EG-XG':3200}
    def __init__(self,PRC,NRC,Send_inf,Rec_inf,scale,S_name,Send_Sen,Rec_Sen,S_0,S_l,S_u,Hy,Ps,If_coup,Coup_S_list1,Coup_S_list1_No,Coup_S_list2,Coup_S_list2_No,Send_HeN,Zr) -> None:
        self.PRC = PRC
        self.NRC = NRC
        self.Send_inf = Send_inf#功率受入片区
        self.Rec_inf = Rec_inf#功率送出片区
        self.scale = scale#出力占比
        self.S_name = S_name
        self.Send_Sen = Send_Sen#功率受入片区对断面的灵敏度
        self.Rec_Sen = Rec_Sen#功率送出片区和全网剩余片区对断面的灵敏度
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
        self.Get_a()
        self.Cal_S()
        pass
    def rl(self):
        tmp_total = sum(self.scale)
        self.RL =  self.scale/tmp_total
        pass
    def Get_a(self):
        Length = len(self.Hy)+len(self.Ps)
        Length_F = len(self.PRC)-len(self.Send_inf)-len(self.Rec_inf)
        a0 = np.zeros((Length_F,Length))
        for i in range(0,Length):
            if i<len(self.Hy):
                a0[self.Hy[i]-1][i] = 1
            else:
                a0[self.Ps[i-len(self.Hy)]-1][i] = 1
        self.a = np.eye(len(self.PRC))
 
        pass

    def Cal_S(self):
        self.cal_S2 = self.Send_Sen
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

        # scenario_List = {'最大供电能力':1,'新能源消纳能力':2,'电力支援能力':3,'水电消纳能力':4,'直流消纳能力':5,'跨区转送':6,'应急功率支撑':7}
        # coef = {'最大供电能力':pl.LpMaximize,'新能源消纳能力':pl.LpMinimize,'电力支援能力':pl.LpMaximize,'水电消纳能力':pl.LpMinimize,'直流消纳能力':pl.LpMinimize,'跨区转送':pl.LpMaximize,'应急功率支撑':pl.LpMaximize}
        # key_list = list(scenario_List.keys())
        # val_list = list(scenario_List.values())
        # scenario_1 = val_list.index(self.scenario)
        Scenario_Solve = pl.LpProblem('跨区转送场景MPC',sense=pl.LpMaximize)
        # 定义辅助变量
        # Var_Z = [pl.LpVariable('辅助变量'+str(i),lowBound = None,upBound= None,cat=pl.LpContinuous) for i in range(0,plant_num)]
        # 定义片区功率调整量
        Var_delta_P = [pl.LpVariable('P'+str(i),lowBound = -plant_lowbounds[i],upBound= plant_upbounds[i],cat=pl.LpContinuous) for i in range(0,plant_num)]


        # 定义目标函数
        tmp_1 = np.zeros((1,self.PRC.shape[0]))
        for i in self.Send_inf:
            tmp_1[0,i-1] = 1
        Object_func = pl.lpSum([tmp_1[0,j]*Var_delta_P[j] for j in range(0,self.PRC.shape[0])])
        for i in self.Rec_inf:
            tmp_1[0,i-1] = 1
        Scenario_Solve += pl.lpSum([tmp_1[0,j]*Var_delta_P[j] for j in range(0,self.PRC.shape[0])]) == 0

        tmp_2 = np.ones((1,self.PRC.shape[0]))
        # 功率平衡约束
        Scenario_Solve += pl.lpSum([tmp_2[0,j]*Var_delta_P[j] for j in range(0,self.PRC.shape[0])]) == 0

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
            Scenario_Solve += (pl.lpSum([(self.PRC[j]-Var_delta_P[j]) for j in range(0,plant_num)]))>=self.Zr[1]+0.1*self.Zr[2]
        elif self.Send_HeN == 3:# 不包括河南省网的情况
            Scenario_Solve += (pl.lpSum([(self.PRC[j]-Var_delta_P[j]) for j in range(0,plant_num)]))>=0*self.Zr[1]+0.1*self.Zr[2]

        # for i in range(0,plant_num):
        #     Scenario_Solve += (Var_Z[i]-Var_delta_P[i]<=0)
        #     Scenario_Solve += (Var_Z[i]-Var_delta_P[i]+1000*(1-Var_bivar[i])>=0)
        #     Scenario_Solve += (Var_Z[i]-Var_bivar[i]*plant_upbounds[i]<=0)
        #     Scenario_Solve += (Var_Z[i]+Var_bivar[i]*plant_lowbounds[i]>=0)
        # 功率调整量为0:，即不采取切负荷的措施
        # if self.scenario>3:
        #     Scenario_Solve += (pl.lpSum(Var_delta_P)==0)
        Scenario_Solve.writeLP('测试')
        # print(pl.listSolvers(onlyAvailable=True))
        # 开始求解
        Scenario_Solve.solve(solver=pl.get_solver('PULP_CBC_CMD'))
        # print(pl.LpStatus[Scenario_Solve.status])
        res_Z = [pl.value(i) for i in Var_delta_P]
        section_later = np.dot(support_sensitivity,np.array(res_Z))+self.S_0
        
        # print(pl.value(Scenario_Solve.objective))
        # print([pl.value(i) for i in Var_bivar])
        # print([pl.value(i) for i in Var_Z])
        best = [res_Z,section_later-self.S_0,section_later,pl.value(Scenario_Solve.objective)]
        #       self.gbest:片区功率调整量   np.dot(aeq,res.x):负荷调减量  section_later:调整后断面功率   adjust_total:断面功率变化量 
        return best
        
        
        pass


class Duanmian:
    def __init__(self) -> None:
        
        

        pass
