from typing import List


class Zone:
    def __init__(self, ID, R, C, Tinit, Pmax, COP, orient, condition, Qall_schedule, Tset_schedule, neighborlist=None):
        '''
        ID: zone number
        neighbors: zone IDs that have heat transfer with the current zone object
        R: thermal resistance ~5C/kW
        C: thermal capacitance ~2-3kWh/C
        Pmax: max heating/cooling system capacity ~2tons
        COP: system efficiency ~3
        Qall: exogenous heat flow (lighting, occupant, solar radiation, misc)
        sf: safety factor for equipment oversize (determines Pmax) ~1.5-2
        Tin: current room temperature
        orient: orientation of the zone (window facing south etc)
        '''
        self.ID = ID
        self.neighbors = []
        self.neighborlist = neighborlist
        self.R = R
        self.C = C
        self.Pmax = Pmax
        self.COP = COP
        self.Qall_schedule = Qall_schedule
        self.Qall = None
        self.Tin = Tinit
        self.orient = orient
        self.P = 0
        self.condition = condition # 1 for heating and -1 for cooling
        self.Tset_schedule = Tset_schedule
        self.Tset = None

        #self.Tout = Toutall[0]
        #self.status = False
        #self.Toutall = Toutall
        #self.Tlow = self.Tset - 0.5
        #self.Thigh = self.Tset + 0.5


    def get_ID(self):
        return self.ID

    def add_neighbor(self, other):
        if other not in self.neighbors:
            self.neighbors.append(other)
            other.neighbors.append(self)

    def add_neighbors(self, neighbors):
        for neighbor in neighbors:
            self.add_neighbor(neighbor)

    def get_neighbors(self):
        for item in self.neighbors:
            yield item.get_ID()
        # return [item.get_ID() for item in self.neighbors]

    def get_current_Tin(self):
        return self.Tin

    def update_Tin(self):
        self.Tin = self.Tset

    def update_Tset(self, step):
        self.Tset = self.Tset_schedule.iloc[step]

    def update_Qall(self, step):
        self.Qall = self.Qall_schedule.iloc[step]

