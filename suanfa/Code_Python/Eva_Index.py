import pandas as pd
import numpy as np
from GetScenario1 import Scenario1 as Sc1
from GetScenario2 import Scenario2 as Sc2
from GetScenario3 import Scenario3 as Sc3
from GetScenario4 import Scenario4 as Sc4
import os as o

class Eva_index:
    GongdianNengli_dianli = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}
    GongdianNengli_dianliang = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}
    ShuidianXiaoNa_Nengli_dianli = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}
    ShuidiannengyuanXiaoNa_Nengli_dianliang = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}
    XinnengyuanXiaoNa_Nengli_dianli = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}
    XinnengyuanXiaoNa_Nengli_dianliang = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}
    ZhiliuXiaoNa_Nengli_dianli = {'河南':None,'湖北':None,'湖南':None,'江西':None,'全网':None}

    def __init__(self,pinaqu_data,S_sen,S0,S_l,S_u,Province,Hy,Ps) -> None:
        self.pianqu_data = pinaqu_data
        self.S_sen = S_sen
        self.S0 = S0
        self.S_l = S_l
        self.S_u = S_u
        self.Province = Province#{'河南':19,'湖北':10,'湖南':6,'江西':7,'全网':42}
        self.Hy = Hy
        self.Ps = Ps
        pass
    def Cal_GongdianNengli(self):
        
        pass

    def Cal_QingjienengyuanXiaoNaNengli(self):
        
        pass
    
    def ZonghetiaojieNaNengli(self):
        
        pass

    def Beiyongjunhengdu(self):
        
        pass