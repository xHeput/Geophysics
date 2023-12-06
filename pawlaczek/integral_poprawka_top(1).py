import pandas as pd
import math
import numpy as np



# import excel file with our data from buffers
wb = pd.read_excel('wejsciowy.xlsx')
pi = math.pi
k = 6.67508 * (10 ** -11) # Newton gravitonal consant
p = 0.2670 # average density of the topographic mass
TCR_results = []
eq_values = []
for n in range(len(wb)):
    r = math.sqrt((wb["X"][n] - wb["Xp"][n]) ** 2 + (wb["Y"][n] - wb["Yp"][n]) ** 2 + (wb["H"][n] - wb["Hnorm"][n]) ** 2) 
    #spherical geocentric radius
    # integration over three variables
    eq = (wb["Xp"][n] * math.log(wb["Yp"][n] + r) + wb["Yp"][n] * math.log(wb["Xp"][n] + r) 
            - ((wb["Hnorm"][n] * math.atan(wb["Xp"][n] * wb["Yp"][n] / (wb["Hnorm"][n] * r))) 
            - (wb["X"][n] * math.log(wb["Y"][n] + r) + wb["Y"][n] * math.log(wb["X"][n] + r)
            - wb["H"][n] * math.atan(wb["X"][n] * wb["Y"][n] / (wb["H"][n] * r)))))
    
    TCR = (k * p * eq) / 100000 # TCR calculation
    eq_values.append(TCR)
    TCR_results.append(np.sum(eq_values)) # Sum of single equations

df=[]
data=[]
for i in range(len(wb)):
    dic = {"ID": wb["OBJECTID_1"][i], 
            "NG": wb["Yp"][i], 
            "EG": wb["Xp"][i],
            "H": wb["H"][i], 
            "g": wb["g"][i],
            "X": wb["Y"][i], 
            "Y": wb["Y"][i], 
            "Hnorm": wb["Hnorm"][i], 
            "Z": wb["Z"][i]}

    data.append(dic)
df = pd.DataFrame(data)

df.insert(9, 'TCR', TCR_results) # Adding TCR to our dataframe
df.to_excel("points_data.xlsx", index=False) # Exporting data to excel
#df.to_csv("points_data.csv", index=False)

print("All done!")

