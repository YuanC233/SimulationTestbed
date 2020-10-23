import numpy as np
from typing import List
from scipy import linalg

PARAM_NAMES = ('Tin', 'P', 'R', 'C', 'Qall', 'Tset')


class System:
    def __init__(self):
        '''
        zonelist: records all zone IDs in this building/system
        syssize: length of the zonelist, determines the size of matrix operation
        Tout: outdoor temperature
        htgload: building heating load
        clgload: building cooling load
        '''
        self.zonelist = []
        self.syssize = 0
        self.all_zone_Tin = None
        self.all_zone_P = None
        self.all_zone_R = None
        self.all_zone_C = None
        self.all_zone_COP = None
        self.all_zone_Qall = None
        self.all_zone_Tset = None
        self.Tout = None
        self.htgload = 0
        self.clgload = 0
        self.A = None
        # self.Tout = Toutall[0]
        # self.Q = Qall[0]
        # self.status = False
        # self.Tset = Tset
        # self.tempP = 0
        # self.signal = None
        # self.allTin = [Tinit]
        # self.runtime = 0

    def update_Tout(self, Tout):
        self.Tout = Tout

    def update_zonelist(self, zones):
        # zones contains a list of zones in the building
        self.zonelist = zones
        self.syssize = len(self.zonelist)

        self.generate_all_zone_params(PARAM_NAMES)
        self.generate_all_zone_COP()
        self.init_A()

    def update_condition_mode(self, condition_mode):
        if condition_mode == 'htg':
            self.htg = True
            self.clg = False
        if condition_mode == 'clg':
            self.clg = True
            self.htg = False

    def generate_all_zone_params(self, names):
        for name in names:
            params = np.zeros((self.syssize, 1))
            for zone in self.zonelist:
                params[zone.ID - 1, 0] = zone.__getattribute__(name)
            self.__setattr__(f'all_zone_{name}', params)

    def update_all_zone_Tin(self):
        Tins = np.zeros((self.syssize, 1))
        for zone in self.zonelist:
            Tins[zone.ID - 1, 0] = zone.Tin
        self.all_zone_Tin = Tins

    def update_all_zone_P(self):
        P = np.zeros((self.syssize, 1))
        for zone in self.zonelist:
            P[zone.ID - 1, 0] = zone.P
        self.all_zone_P = P

    def get_all_zone_Tin(self):
        return self.all_zone_Tin

    def get_all_zone_P(self):
        return self.all_zone_P

    def get_all_zone_R(self):
        return self.all_zone_R

    def get_all_zone_C(self):
        return self.all_zone_C

    def get_all_zone_Qall(self):
        return self.all_zone_Qall

    def get_all_zone_Tset(self):
        return self.all_zone_Tset

    def generate_all_zone_COP(self):
        # COP is positive for heating, and negative for cooling
        COP = np.zeros((self.syssize, 1))
        for zone in self.zonelist:
            COP[zone.ID - 1, 0] = zone.COP * zone.condition
        self.all_zone_COP = COP

    def get_all_zone_COP(self):
        return self.all_zone_COP

    def generate_Rij(self, wallR=70):  # Assume R-13 wall with an effective area of 30m2
        Rij = np.zeros((self.syssize, self.syssize))
        for zone in self.zonelist:
            # define diagnal as 1/Ri
            Rij[zone.ID - 1, zone.ID - 1] = 1. / zone.R
            # fill in the adjacency matrix from neighbor info
            for zone_j in zone.neighbors:
                Rij[zone.ID - 1, zone_j.ID - 1] = 1. / wallR
        for i in range(self.syssize):
            Rij[i, i] = -Rij[i, :].sum()
        return Rij

    # continuous-time system dynamics equation
    # Tdot = AT + BP + w
    # T is zone indoor temp, P is power

    def init_A(self):
        C = self.get_all_zone_C()
        C = np.broadcast_to(C, (self.syssize, self.syssize)).T
        A = np.multiply(1./C, self.generate_Rij())
        self.A = A

    def get_A(self):
        return self.A

    def get_B(self):
        COP = self.get_all_zone_COP()
        C = self.get_all_zone_C()
        bi = np.squeeze(np.divide(COP, C))
        B = np.diag(bi)
        return B

    def get_W(self):
        theta = self.Tout * np.ones((self.syssize, 1))
        R = self.get_all_zone_R()
        Q = self.get_all_zone_Qall()
        C = self.get_all_zone_C()
        W = np.divide(theta, np.multiply(C, R)) + np.divide(Q, C)
        return W

    def discrete_systemT_update(self, deltaT):
        A = self.get_A()
        B = self.get_B()
        W = self.get_W()
        Ad = linalg.expm(np.multiply(deltaT, A))
        Bd = np.dot(np.linalg.inv(A), np.dot((Ad - np.identity(self.syssize)), B))
        Wd = np.dot(np.linalg.inv(A), np.dot((Ad - np.identity(self.syssize)), W))
        Tk = self.get_all_zone_Tin()
        U = self.get_all_zone_P()
        Tk1 = np.dot(Ad, Tk) + np.dot(Bd, U) + Wd
        return Tk1

    def load_calculation(self, deltaT):
        A = self.get_A()
        B = self.get_B()
        W = self.get_W()
        Ad = linalg.expm(np.multiply(deltaT, A))
        Bd = np.dot(np.linalg.inv(A), np.dot((Ad - np.identity(self.syssize)), B))
        Wd = np.dot(np.linalg.inv(A), np.dot((Ad - np.identity(self.syssize)), W))
        Tk = self.get_all_zone_Tin()
        Tset = self.get_all_zone_Tset()
        P = np.dot(np.linalg.inv(Bd), (Tset - np.dot(Ad, Tk) - Wd))
        return P











