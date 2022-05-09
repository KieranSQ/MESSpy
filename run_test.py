from rec import REC
from economics import NPV
import time
import os
import json

#%%

"""
MESSpy - Run
"""

#study_case = 'Bs 10kWh p2'
#study_case = 'B 10kWh p2' # str name for results file.pkl
study_case = 'only pv' # str name for results file.pkl
reference_case = 'reference case' # str name for results file.pkl

#file = 'structure_bs.json'
#file = 'structure_b.json'
file = 'structure.json'

"""
Input files
"""

path = r'./inputs'


filepath = os.path.join(path,file)
with open(filepath,'r') as f:
    structure = json.load(f)

file = 'general.json'
filepath = os.path.join(path,file)
with open(filepath,'r') as f:
    general = json.load(f)

time1 = time.time()
 
print('Creating structure..')
# Creating initial structure
rec = REC(structure,general) # create REC structure

time2 = time.time()
print('Structure created in {:.2f} seconds'.format(time2-time1))

#%% ###########################################################################
print('Running the model..')
time2 = time.time()


# Running the model
#rec.reset() # reset REC energy balances
rec.REC_energy_simulation() # simulate REC structure
rec.save(study_case) # save results in 'study_case.pkl'

time3 = time.time()
print('Model runned in {:.2f} seconds'.format(time3-time2))
  

#%% ###########################################################################
print('Economic analysis..') 
time3 = time.time()

file = 'economics.json'
filepath = os.path.join(path,file)
with open(filepath,'r') as f:
    economic_data = json.load(f)

file = 'refcase.json'
filepath = os.path.join(path,file)
with open(filepath,'r') as f:
    structure0 = json.load(f)
    
# Reference case simulation (run only if changed)
rec0 = REC(structure0,general) # create REC
rec0.REC_energy_simulation() # simulate REC 
rec0.save(reference_case) # save results in 'reference_case.pkl'

# Actual economic analysis (It has no sense if simulation_years = 1)
NPV(structure,structure0,study_case,reference_case,economic_data,general['simulation years']) 

time4 = time.time()  
print('Eonomic analysis performend in {:.2f} seconds'.format(time4-time3))

#%% post process
import postprocess as pp
import numpy as np
#print('Post processing..')
time4 = time.time()

#study_case = 'Bs 10kWh p2'
#study_case = 'B 10kWh p2' # str name for results file.pkl
#study_case = 'only pv' # str name for results file.pkl

# p2 43

#pp.total_balances(study_case,'p2')
#pp.LOC_plot(study_case)
pp.NPV_plot(study_case)
pp.Flows(study_case)

# =============================================================================
# for first_day in [43] :
#     last_day=first_day
#     #pp.hourly_balances(study_case,'p1', first_day, last_day)
#    
#     study_case = 'only pv'
#     pp.hourly_balances(study_case,'p1', first_day, last_day, collective=0)
#     study_case = 'B 10kWh p2'
#     pp.hourly_balances(study_case,'p1', first_day, last_day, collective=0)
#     study_case = 'Bs 10kWh p2'
#     pp.hourly_balances(study_case,'p1', first_day, last_day, collective=1)
# =============================================================================
  
# =============================================================================
# pp.hourly_balances(study_case,'p3', first_day, last_day)
# pp.hourly_balances(study_case,'c1', first_day, last_day)
# pp.hourly_balances(study_case,'c2', first_day, last_day)
# pp.hourly_balances(study_case,'c3', first_day, last_day)
# pp.hourly_balances(study_case,'c4', first_day, last_day)
# pp.hourly_balances(study_case,'c5', first_day, last_day)
# =============================================================================

#pp.csc_allocation_sum(study_case)
time5 = time.time()  
#print('Post process performend in {:.2f} seconds'.format(time5-time4))

# =============================================================================
# for h,v in enumerate(rec.energy_balance['electricity']['into grid']):
#     if - v - rec.energy_balance['electricity']['from grid'][h] >0:
#         print(h)
# =============================================================================
    


