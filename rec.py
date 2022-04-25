import numpy as np
import pickle
import os
from location import location

class REC:
    
    def __init__(self,structure,general):
        """
        Create a Renewable Energy Comunity object composed of several locations (producers, consumers, prosumers)
    
        structure : dictionary (all the inputs are optional)
            'location_1_name': inputs required to create a location object (see Location.py)
            'location_2_name': 
                ...
            'location_n_name':
                
        general : dictionary
            'simulation years': number of years to be simulated
            'latitude': float
            'longitude': float
            'reference year': int year [2005 - 2015] used for output data and to get data from PVGIS if TMY = False
            'TMY': bool true if data of TMY is to be used              
                        
        output : REC object able to:
            simulate the energy flows of each present locations .REC_simulation
            record REC energy balances .energy_balance (electricity, heat, cool, gas and hydrogen) 
        """

        self.locations = {} # initialise REC locations dictionary
        self.energy_balance = {'electricity': {}, 'heat': {}, 'cool': {}, 'hydrogen': {}, 'gas': {}} # initialise energy balances dictionaries of each energy carrier
        
        self.simulation_hours = int(general['simulation years']*8760) # hourly timestep  
        
        ### create location objects and add them to the REC locations dictionary
        for location_name in structure: # location_name are the keys of 'structure' dictionary and will be used as keys of REC 'locations' dictionary too
            self.locations[location_name] = location(structure[location_name],general,location_name) # create location object and add it to REC 'locations' dictionary                
            
                  
    def REC_energy_simulation(self):
        """
        Simulate the REC every hour
        
        output :
            updating location energy balances
            updating REC energy balances
        """
        
        ### initialise REC electricity balances
        self.energy_balance['electricity']['from grid'] = np.zeros(self.simulation_hours) # array of electricity withdrawn from the grid from the whole rec
        self.energy_balance['electricity']['into grid'] = np.zeros(self.simulation_hours) # array of electricity withdrawn from the grid
        self.energy_balance['electricity']['collective self consumption'] = np.zeros(self.simulation_hours) # array of collective self consumed electricity from the whole rec
        
        for h in range(self.simulation_hours): # h: hour to simulate from 0 to simulation_hours 
            for location_name in self.locations: # each locations 
                self.locations[location_name].loc_energy_simulation(h) # simulate a single location updating its energy balances
                
            ### solve electricity grid 
                if self.locations[location_name].energy_balance['electricity']['grid'][h] < 0:
                    self.energy_balance['electricity']['into grid'][h] += self.locations[location_name].energy_balance['electricity']['grid'][h] # electricity fed into the grid from the whole rec at hour h
                else:                                                     
                    self.energy_balance['electricity']['from grid'][h] += self.locations[location_name].energy_balance['electricity']['grid'][h] # electricity withdrawn from the grid the whole rec at hour h
                
            ### solve smart batteries
            for location_name in self.locations:
                
                # collective = 1: REC tels to location how mutch energy could be stored in the battery every hour
                # if the location has a smart battery type 1 and it is feeding electricity into the grid at hour h
                
                if 'battery' in self.locations[location_name].technologies and self.locations[location_name].technologies['battery'].collective == 1 and self.locations[location_name].energy_balance['electricity']['grid'][h] < 0:
                    
                    # the location can stored in his battery the minimin beetwen how mutch it's feeding into the grid and how mutch it's not useful for collective self consumption 
                    E = min(-self.locations[location_name].energy_balance['electricity']['grid'][h], -self.energy_balance['electricity']['into grid'][h] - self.energy_balance['electricity']['from grid'][h])
                    E = max(0,E) # only charging
                    self.locations[location_name].energy_balance['electricity']['battery'][h] = self.locations[location_name].technologies['battery'].use(h,E) # electricity absorbed(-) by battery
                    self.locations[location_name].energy_balance['electricity']['grid'][h] += - self.locations[location_name].energy_balance['electricity']['battery'][h] # update grid balance (locatiom)
                    self.energy_balance['electricity']['into grid'][h] += - self.locations[location_name].energy_balance['electricity']['battery'][h] # update grid balan ce (rec)
                
                ### if there are more then one battery with .collective == 1 ???
                    ## proportion redistribution to add
                    
                ### collective battery    
                if 'battery' in self.locations[location_name].technologies and self.locations[location_name].technologies['battery'].collective == 2:
                    pass
                    
                    
                
            ### calculate collective self consumption
            self.energy_balance['electricity']['collective self consumption'][h] = min(-self.energy_balance['electricity']['into grid'][h],self.energy_balance['electricity']['from grid'][h]) # calculate REC collective self consumption how regulation establishes      


    def save(self,simulation_name):
        """
        Save REC and each location energy balances
        
        simulationa_name : str 
        
        output: 
            balances/simulation_name.pkl
            soc/simulation_name.pkl
        """
        
        balances = {}
        SOC = {}
        balances['REC'] = self.energy_balance
        
        for location_name in self.locations:
            balances[location_name] = self.locations[location_name].energy_balance
            
            SOC[location_name] = {}
            
            tech_name = 'battery'
            if tech_name in self.locations[location_name].technologies:
                SOC[location_name][tech_name] = self.locations[location_name].technologies[tech_name].SOC
        
            tech_name = 'H tank'
            if tech_name in self.locations[location_name].technologies:
                SOC[location_name][tech_name] = self.locations[location_name].technologies[tech_name].SOC_volume()
        
        directory = './results'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open('results/balances_'+simulation_name+".pkl", 'wb') as f:
            pickle.dump(balances, f) 
            
        with open('results/SOC_'+simulation_name+".pkl", 'wb') as f:
            pickle.dump(SOC, f) 
            
            
    def reset(self):
        """
        Use this function before a new simulation if you don't want to recreate the rec object
        
        output: initialise SOC
        """
        
        to_reset = ['battery','H tank'] # technologies for which the SOC must be reset
        for location_name in self.locations: # each location
            for tech_name in to_reset:
                if tech_name in self.locations[location_name].technologies: 
                    self.locations[location_name].technologies[tech_name].SOC = np.zeros(self.simulation_hours+1) # array State of Charge 
                    self.locations[location_name].technologies[tech_name].used_capacity = 0 # used capacity <= max_capacity   
    
        
   