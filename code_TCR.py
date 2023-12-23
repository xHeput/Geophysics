import pandas as pd
import math
import numpy as np

# Import Excel file with our data from buffer with 1200 m radius from buffers with measurment and DTM data
df = pd.read_excel('buffor_table_v2.xlsx')

# Variables to group data with id's of objects
indexes_data = df["OBJECTID_1"]
hnorm_data = df["Hnorm"]
hp_data = df["H"]

# Arrays to storage individual data each of measure point
objectids_table = []
h_values_table = []
hp_values_table = []
n_of_pts_in_buff = []

# Create tables with grouped data for object id's
for n in range(len(df["OBJECTID_1"])):
    # Append current values into value arrays
    objectids_table.append(indexes_data[n])
    h_values_table.append(hnorm_data[n])  # height in each buffer
    hp_values_table.append(hp_data[n])  # height of each measure point
    n_of_pts_in_buff.append(n)  # number of slices in each buffer

k = 6.67508 * (10 ** -11)  # Newton gravitonal consant [m3/kg*s2]
p = 2670  # average density of the topographic mass [kg/m3]
r = 0  # the length of the initial radius limiting the slice [m]
r2 = 1200  # the length of the final radius limiting the slice [m]
pi = math.pi  # pi constant

h_diff_table = []  # array to storage terrain height mean of each slice relative to measure point height
TCR_result = []  # array to storage TCR final values

# TCR equation loop
for i in range(len(objectids_table)):
    H = hp_values_table[i]  # H value of each point
    Hnorm = h_values_table[i]  # Mean h value of terrain
    n = n_of_pts_in_buff[i]  # Number of slices in buffer
    h_diff = abs(round(Hnorm - H,6))  # Difference between height of terrain and point
    h_diff_table.append(h_diff)  # Add difference to array

    # TCR - method for a cylinder
    eq = np.sum(r2 - r + math.sqrt(r**2 + h_diff**2) - math.sqrt(r2 ** 2 + h_diff ** 2))
    if n != 0:
        TCR = ((2/n)*pi*k*p * eq) * 10**5
    else:
        TCR = 0
    TCR_result.append(TCR)  # Adding TCRs to storage array


df2 = []
data = []

# data frame creation
for i in range(len(df)):
    dic = {"ID": df["OBJECTID_1"][i], 
            "NG": df["Yp"][i], 
            "EG": df["Xp"][i],
            "H": df["H"][i], 
            "g": df["g"][i],}

    data.append(dic)
df2 = pd.DataFrame(data)



df2.insert(5, 'TCR',TCR_result)  # Adding TCR to our dataframe
df2.insert(6,'Hnorm',h_values_table)  # Adding terrain mean to our dataframe
df2.insert(7,'Height_diff',h_diff_table)  # Adding heights difference to dataframe
df2.to_excel("dane_graw_tcr_v2.xlsx", index=False)  # Exporting dataframe to excel
df2.to_csv("dane_graw_tcr_v2.csv", index=False)  # Exporting dataframe to excel