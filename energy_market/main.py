import os
import pandas as pd


from EUnix.simulation import Simulation as sm

marktSlots = "timeslot" #This is the user name
curr_dir = os.path.dirname(__file__)


data = pd.read_csv(os.path.join(curr_dir, "data/"+str(marktSlots)+'.csv'), delimiter=',')



Nslot = 94
startSlot = "2014-12-01T00:00"
grid_fee = 2 #grid fee in cent/kWh
simu = sm(data,startSlot, Nslot, "p2p", grid_fee) #mechanism can be "uniform", "p2p", "hhc"
#simu = sm(pub_ins)
prev_slot, index = simu.simulate()
simu.closeSimulation(prev_slot, index)



