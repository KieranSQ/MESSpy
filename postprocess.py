"""
Post processing
"""
import pickle
import numpy as np
import matplotlib.pyplot as plt
import plotly.io as pio
import plotly.graph_objects as go


def total_balances(simulation_name):

    with open('Results/balances_'+simulation_name+'.pkl', 'rb') as f:
        balances = pickle.load(f)
    
    ###### load analysys
    
    ##### total electricity balances
    carriers = ['electricity']
    units = {'electricity': 'kWh', 'hydrogen': 'kg'}
    
    for carrier in carriers:
        print('\nTotal '+carrier+' balances:\n')
        for loc in balances:
            print('\n'+loc)   
            for b in balances[loc][carrier]:
                
                positiv=balances[loc][carrier][b][balances[loc][carrier][b]>0].sum()
                negativ=balances[loc][carrier][b][balances[loc][carrier][b]<0].sum()
                
                if positiv != 0:
                    print(b+' '+str(round(positiv,1))+' '+units[carrier])
                    
                if negativ != 0:
                    print(b+' '+str(round(negativ,1))+' '+units[carrier])
    print('\n')
   
    
def NPV_plot():
    ##### economic
    simulation_name = 'economic_assessment'
    with open('Results/'+simulation_name+'.pkl', 'rb') as f:
        economic = pickle.load(f)
    
    plt.figure(dpi=1000)
    
    for loc in economic:    
        y = economic[loc]['NPV']
        x = np.linspace(0,len(y)-1,len(y))
        plt.plot(x,y,label=loc)
        
    plt.legend()
    plt.title("Investments")
    plt.grid()
    plt.ylabel('Net Present Value [€]')
    plt.xlabel('Time [years]')
    plt.xlim(0,len(y)-1)
    #plt.ylim(-12000,12000)
    plt.show()
    
    
def LOC_plot(simulation_name):
      
    with open('Results/LOC_'+simulation_name+'.pkl', 'rb') as f:
        LOC = pickle.load(f)
           
    unit = {'H tank': '[m3]', 'battery': '[kWh]'}
    
    for location_name in LOC:
        for tech in LOC[location_name]:
            
            y = LOC[location_name][tech]
            x = np.linspace(0,len(y)-1,len(y))        
            plt.plot(x,y,label=location_name)
            plt.grid()
            plt.ylabel('LOC '+unit[tech])
            plt.xlabel('Time [hours]')
            plt.title(location_name+' '+tech)
            plt.show()
        

def Flows(simulation_name,carrier='electricity'):

    pio.renderers.default='browser'
    with open('Results/balances_'+simulation_name+'.pkl', 'rb') as f:
        balances = pickle.load(f)
    
    ### data prepearing
    node_label = ["transformer","transformer","grid"]
    node_color = ['silver','silver','gray']
    source = []
    target = []
    value = []
    link_color = []
    link_label = []
        
    ### add from grid
    node_number = 3
    for loc in balances:
        if loc != 'REC':
            
            node_color.append('brown')
            node_label.append('load '+loc)
            
            source.append(0)
            target.append(node_number)
            value.append(np.sum(balances[loc][carrier]['grid'], where = balances[loc][carrier]['grid'] > 0))
            link_color.append('tomato')
            link_label.append('from grid')
            node_number += 1
    value.append(sum(value)-sum(balances['REC'][carrier]['collective self consumption']))
    source.append(2)
    target.append(0)
    link_color.append('tomato')
    link_label.append('from grid')
    
    ### add to grid and self consumption
    node_number2 = 3
    for loc in balances:
        if loc != 'REC':
            if 'PV' in balances[loc][carrier]:
            
                node_color.append('skyblue')
                node_label.append('PV '+loc)
                
                # into grid
                source.append(node_number)
                target.append(1)
                value.append(- (np.sum(balances[loc][carrier]['grid'], where = balances[loc][carrier]['grid'] < 0)))
                link_color.append('cornflowerblue')
                link_label.append('to grid')
                
                # self consumption
                source.append(node_number)
                target.append(node_number2)
                
                if 'battery' in balances[loc][carrier]:
                    value.append(-np.sum(balances[loc][carrier]['demand']) - np.sum(balances[loc][carrier]['grid'], where = balances[loc][carrier]['grid'] > 0) -np.sum(balances[loc][carrier]['battery'], where = balances[loc][carrier]['battery'] > 0))
                    link_color.append('yellowgreen')
                    link_label.append('self consumption (directly from PV)')
                    node_number += 1
                    
                    node_color.append('plum')
                    node_label.append('battery '+loc)
                    
                    source.append(node_number)
                    target.append(node_number2)
                    value.append(np.sum(balances[loc][carrier]['battery'], where = balances[loc][carrier]['battery'] > 0))
                    link_color.append('purple')
                    link_label.append('self consumption (from battery)')
                    
                    source.append(node_number-1)
                    target.append(node_number)
                    value.append(-np.sum(balances[loc][carrier]['battery'], where = balances[loc][carrier]['battery'] < 0))
                    link_color.append('violet')
                    link_label.append('to battery')   
                    
                    node_number += 1
                    
                elif 'electrolyzer' in balances[loc][carrier] and 'fuel cell' in balances[loc][carrier]:
                    value.append(-np.sum(balances[loc][carrier]['demand']) - np.sum(balances[loc][carrier]['grid'], where = balances[loc][carrier]['grid'] > 0) -np.sum(balances[loc][carrier]['fuel cell']))
                    link_color.append('yellowgreen')
                    link_label.append('self consumption (directly from PV)')
                    node_number += 1
                    
                    node_color.append('sandybrown')
                    node_label.append('hydrogen '+loc)
                    
                    source.append(node_number)
                    target.append(node_number2)
                    value.append(np.sum(balances[loc][carrier]['fuel cell']))
                    link_color.append('peru')
                    link_label.append('self consumption (from fuel cell)')
                    
                    source.append(node_number-1)
                    target.append(node_number)
                    value.append(-np.sum(balances[loc][carrier]['electrolyzer']))
                    link_color.append('chocolate')
                    link_label.append('to electrolyzer')   
                    
                    node_number += 1
                                        
                else:
                    value.append(-np.sum(balances[loc][carrier]['demand']) - np.sum(balances[loc][carrier]['grid'], where = balances[loc][carrier]['grid'] > 0))
                
                    link_color.append('yellowgreen')
                    link_label.append('self consumption')
                    node_number += 1
                    
                    
                    
                node_number2 += 1 # load
                
    ### LV to MV
    source.append(1)
    source.append(1)
    target.append(0)
    target.append(2)
    value.append(sum(balances['REC'][carrier]['collective self consumption'])) 
    value.append(- np.sum(balances['REC'][carrier]['into grid'])-sum(balances['REC'][carrier]['collective self consumption']))   
    link_color.append('gold')
    link_label.append('collective self consumption')
    link_color.append('orange')
    link_label.append('to grid')
                
    fig = go.Figure(data=[go.Sankey(
        valueformat = ".1f",
        valuesuffix = " kWh",
        arrangement = "snap",
        node = {
                'thickness': 30,
                #'line': dict(color = "black", width = 0.5),
                'label': node_label,
                'color': node_color,
                "x": [0.7,0.3,0.5],
                "y": [0.1,0.1,0.25], # stranamente è ribaltata rispetto ad annotations
                'pad': 100
                },
        link = {
                'source': source, # indices correspond to labels, eg A1, A2, A1, B1, ...
                'target': target,
                'value': value,
                'color': link_color,
                'label': link_label
                })])
    
    fig.update_layout(title_text="Energy flows", font_size=25,
                      annotations=[dict(
                          x=0.,
                          y=0.,
                          text='',
                          showarrow=False
                          )] )
    fig.write_html(f"Results/energy_flows_{simulation_name}.html")
    fig.show()

 
def hourly_balances(simulation_name,location_name,first_day,last_day,carrier='electricity',width=0.9,collective=0):
    
        with open('Results/balances_'+simulation_name+'.pkl', 'rb') as f:
            balances = pickle.load(f)
            
        balances = balances[location_name][carrier]
        
        if 'demand' in balances:
            load = -balances['demand'][first_day*24:last_day*24+24]
        
        if 'PV' in balances:
            pv = balances['PV'][first_day*24:last_day*24+24]
            
        if 'grid' in balances:                
            into_grid = np.zeros(24*(last_day-first_day+1))
            from_grid = np.zeros(24*(last_day-first_day+1)) 
            for i,e in enumerate(balances['grid'][first_day*24:last_day*24+24]):
                if e > 0:
                    from_grid[i] = e
                else:
                    into_grid[i] = e 
        
        if 'battery' in balances:
            charge_battery = np.zeros(24*(last_day-first_day+1))
            discharge_battery = np.zeros(24*(last_day-first_day+1))
            for i,e in enumerate(balances['battery'][first_day*24:last_day*24+24]):
                if e > 0:
                    discharge_battery[i] = e
                else:
                    charge_battery[i] = e 
                    
        if 'electrolyzer' in balances and 'fuel cell' in balances:
            fc = balances['fuel cell'][first_day*24:last_day*24+24]
            ele = balances['electrolyzer'][first_day*24:last_day*24+24]
                     
        to_csc = np.zeros(24*(last_day-first_day+1))
        from_csc = np.zeros(24*(last_day-first_day+1))
        for i,e in enumerate(balances['collective self consumption'][first_day*24:last_day*24+24]):
            if e > 0:
                from_csc[i] = e
            else:
                to_csc[i] = e 
            
        x = np.linspace(first_day*24+1,(last_day+1)*24,(last_day-first_day+1)*24)
        x = np.arange((last_day-first_day+1)*24)
        
        fig = plt.figure(dpi=1000)
        from mpl_toolkits.axisartist.axislines import SubplotZero
        ax = SubplotZero(fig, 1, 1, 1)
        fig.add_subplot(ax)
        ax.axis["xzero"].set_visible(True)
        for n in ["bottom", "top", "right"]:
            ax.axis[n].set_visible(False)
        ax.grid(axis='y')
        
        if 'PV' in balances:
            ax.bar(x, np.minimum(load,pv), width,  label='PV self consumption', color='yellowgreen')
            ax.bar(x, np.maximum(pv-load,np.zeros(len(pv))), width, bottom=load, label='PV surplus', color='cornflowerblue')
            
            if not 'battery' in balances and not 'electrolyzer' in balances:
                ax.bar(x, from_grid-from_csc, width ,bottom=pv+from_csc, label='from grid', color='tomato')
                ax.bar(x, np.array(from_csc), width, bottom=pv,  color='gold')
            
                ax.bar(x, np.array(into_grid), width, label='into grid', color='orange')
                ax.bar(x, np.array(to_csc), width, label='collective self consumption',  color='gold')
                
            if 'battery' in balances:
                ax.bar(x, from_grid-from_csc, width, bottom=pv+discharge_battery+from_csc, label='from grid', color='tomato')
                ax.bar(x, np.array(from_csc), width, bottom=discharge_battery+pv,  color='gold')
                ax.bar(x, discharge_battery, width, bottom = pv, label='discharge battery',  color='purple')
                
                ax.bar(x, np.array(into_grid), width, bottom=charge_battery , label='into grid', color='orange')
                if collective == 0:
                    ax.bar(x, np.array(charge_battery), width,  label='charge battery',  color='violet')
                    ax.bar(x, np.array(to_csc), width, bottom=charge_battery, label='collective self consumption',  color='gold')
                else:
                    ax.bar(x, np.array(charge_battery), width, bottom=np.array(to_csc),  label='charge battery',  color='violet')
                    ax.bar(x, np.array(to_csc), width, label='collective self consumption',  color='gold')
                    
            if 'electrolyzer' in balances and 'fuel cell' in balances:
                ax.bar(x, from_grid-from_csc, width ,bottom=pv+fc+from_csc, label='from grid', color='tomato')
                ax.bar(x, np.array(from_csc), width, bottom=pv+fc,  color='y')
            
                ax.bar(x, np.array(into_grid), width,bottom=ele , label='into grid', color='orange')
                ax.bar(x, np.array(ele), width,  label='to electrolyzer',  color='chocolate')
                ax.bar(x, fc, width, bottom = pv, label='from fuel cell',  color='peru')
                ax.bar(x, np.array(to_csc), width, bottom=ele, label='collective self consumption',  color='gold')
            
            plt.ylim(-4,4)
            
        else:
            ax.bar(x, from_grid-from_csc, width ,bottom=from_csc, label='from grid', color='tomato')
            ax.bar(x, np.array(from_csc), width, label='collective self consumption',  color='gold')
            plt.ylim(0,3.3)
        
        plt.title(location_name+' '+str(first_day))
        plt.plot(x,load,'k',label='load')     
        #plt.legend(ncol=3, bbox_to_anchor=(1.2, 0))
        plt.ylabel("Hourly energy [kWh/h] ")
        #plt.xticks([0,6,12,18,24],['0','6','12','18','24'],fontsize=10,color='g')
        #plt.xticks([0,6,12,18,24,30,36,42,48],['0','6','12','18','24','30','36','42','48'],fontsize=10,color='g')
        #plt.yticks([-2,-1,0,1,2],['-2','-1','0','1','2'])
        plt.show()
        
            
def csc_allocation_sum(simulation_name):
    with open('Results/balances_'+simulation_name+'.pkl', 'rb') as f:
        balances = pickle.load(f)
        
    for location_name in balances:
        csc = balances[location_name]['electricity']['collective self consumption']
        from_csc = csc.sum(where=csc>0)
        to_csc = csc.sum(where=csc<0)
    
        print(f"{location_name} {int(from_csc)}  {int(to_csc)}")
   
    
        
        
