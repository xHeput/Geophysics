import pandas as pd
import math
import numpy as np

# mathematical formula #1.1
def freeair_anomaly(h):
    return 0.3086 * h

# mathematical formula #1.2
def gravity_intensity(g, delta_gh):
    return g + delta_gh

# mathematical formula #2.1
def bouger_anomaly_gf(delta_gh, p, h):
    return delta_gh + (0.04187 * p * h)

# mathematical formula #2.2
def gravity_value_bouger_anomaly_gf(g, delta_gB):
    return g + delta_gB

# mathematical formula #2.3
def incomplete_gravity_value_bouger_anomaly_gf(g0e, gamma0):
    return g0e - gamma0

# mathematical formula #3.1
def TCR(wb, k, p):
    for n in range(len(wb)):
        r = math.sqrt((wb["X"][n] - wb["Xp"][n]) ** 2 + (wb["Y"][n] - wb["Yp"][n]) ** 2 + (wb["H"][n] - wb["Hnorm"][n]) ** 2) 
        #spherical geocentric radius
        # integration over three variables
        eq = (wb["Xp"][n] * math.log(wb["Yp"][n] + r) + wb["Yp"][n] * math.log(wb["Xp"][n] + r) 
                - ((wb["Hnorm"][n] * math.atan(wb["Xp"][n] * wb["Yp"][n] / (wb["Hnorm"][n] * r))) 
                - (wb["X"][n] * math.log(wb["Y"][n] + r) + wb["Y"][n] * math.log(wb["X"][n] + r)
                - wb["H"][n] * math.atan(wb["X"][n] * wb["Y"][n] / (wb["H"][n] * r)))))
        
    return (k * p * eq) / 100000

# mathematical formula #3.1.1
def full_bouger_anomaly_gravity(delta_gt, p, h):
    return delta_gt + (0.3086 * h) - (0.04187 * p * h)

# mathematical formula #4
def normal_gravity(fi):
    return 978032.67715 * (1 + 0.00530244 * math.sin(fi)**2 - 0.0000058495 * math.sin(2 * fi)**2) #[mGal] B => fi

def gravity_intensity_reduced(g, delta_gB):
    return g + delta_gB

def full_gravity_intensity_reduced(g0_prim_prim, B):
    return g0_prim_prim - normal_gravity(B)

# import excel file with our data from buffers
wb = pd.read_excel('raw_data_cleaned.xlsx')
# variables
pi = math.pi
k = 6.67508 * (10 ** -11) # Newton gravitonal consant
p = 0.2670 # average density of the topographic mass
TCR_results = []
eq_values = []
df=[]
data=[]
delta_gh = []
go_prim = []
delta_go_prim = []
gamma0 = []
delta_gB = []
g0e = []
delta_g0e = []
delta_gB_TCR = []
g0_prim_prim = []
delta_g0_prim_prim = []

# data frame creation
for i in range(len(wb)):
    dic = {"ID": wb["OBJECTID_1"][i], 
            "NG": wb["Yp"][i], 
            "EG": wb["Xp"][i],
            "H": wb["H"][i], 
            "g": wb["g"][i],
            "B": wb["B"][i],
            "L": wb["L"][i]}

    data.append(dic)
df = pd.DataFrame(data)

# mathematical formula #4
for n in range(len(wb)):
    gamma0.append(normal_gravity(wb["B"][n]))



# mathematical formula #1.1
for n in range(len(wb)):
    delta_gh.append(freeair_anomaly(wb["H"][n]))

df.insert(7, 'delta_gh', delta_gh) 

# mathematical formula #1.2
for n in range(len(wb)):
    go_prim.append(gravity_intensity(wb["g"][n],delta_gh[n]))

df.insert(8, 'go_prim', go_prim) 

# mathematical formula #1.3
for n in range(len(wb)):
    delta_go_prim.append(gravity_intensity(go_prim[n],gamma0[n]))

df.insert(9, 'delta_go_prim', delta_go_prim) 

# mathematical formula #2.1
for n in range(len(wb)):
    delta_gB.append(bouger_anomaly_gf(delta_gh[n], p, wb["H"][n]))

df.insert(10, 'delta_gB', delta_gB) 

# mathematical formula #2.2
for n in range(len(wb)):
    g0e.append(gravity_value_bouger_anomaly_gf(wb["g"][n], delta_gB[n]))

df.insert(11, 'g0e', g0e)     

# mathematical formula #2.3
for n in range(len(wb)):
    delta_g0e.append(incomplete_gravity_value_bouger_anomaly_gf(g0e[n], gamma0[n]))

df.insert(12, 'delta_g0e', delta_g0e)   

# mathematical formula #3.1
for n in range(len(wb)):
    eq_values.append(TCR(wb, k, p))
    TCR_results.append(np.sum(eq_values)) # Sum of single equations

df.insert(13, 'TCR', TCR_results) # Adding TCR to our dataframe

# mathematical formula #3.1.1
for n in range(len(df)):
    delta_gB_TCR.append(full_bouger_anomaly_gravity(df["TCR"][n], p, df["H"][n]))

df.insert(14, 'delta_gB_TCR', delta_gB_TCR)   

# mathematical formula #3.2
for n in range(len(df)):
    g0_prim_prim.append(gravity_intensity_reduced(df["g"][n], delta_gB_TCR[n]))

df.insert(15, "g0''", g0_prim_prim) # Adding TCR to our dataframe

# mathematical formula #3.3
for n in range(len(df)):
    delta_g0_prim_prim.append(full_gravity_intensity_reduced(g0_prim_prim[n], wb["B"][n]))

df.insert(16, "delta_g0''", delta_g0_prim_prim) # Adding TCR to our dataframe


df.to_excel("points_data.xlsx", index=False) # Exporting data to excel
df.to_csv("points_data.csv", index=False)



print("All Done!")