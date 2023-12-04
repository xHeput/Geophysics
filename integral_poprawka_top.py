import pandas as pd
import math
import numpy as np

# import excel file
wb = pd.read_excel('buffor_table.xlsx')

# variables
bufor_point = []
index_table = wb["OBJECTID_1"]
h_table_excel = wb["Hnorm"]
x_table_excel = wb["X"]
y_table_excel = wb["Y"]
z_table_excel = wb["Z"]

h_mean = 0
x_mean = 0
y_mean = 0
z_mean = 0
objectid = 0

h_table = []
x_table = []
y_table = []
z_table = []
objectid_table = []
counter = 0
x = index_table[0]


data = []
xp_table = []
yp_table = []
g_table = []
hp_table = []
duplicate_dict = {}

# create tables with means for objectid
for n in range(len(wb["OBJECTID_1"])):
    # checks value for certain objectid
    if x == index_table[n]:
        # makes containers for mean calcs
        objectid += index_table[n]
        h_mean += h_table_excel[n]
        x_mean += x_table_excel[n]
        y_mean += y_table_excel[n]
        z_mean += z_table_excel[n]

        # keeps track number of components
        counter += 1
    else:
        # calc mean and append into table
        objectid_table.append(objectid / counter)
        h_table.append(round(h_mean / counter, 3))
        x_table.append(round(x_mean / counter, 3))
        y_table.append(round(y_mean / counter, 3))
        z_table.append(round(z_mean / counter, 3))

        # reset
        counter = 1
        x = index_table[n]
        objectid = index_table[n]
        h_mean = h_table_excel[n]
        x_mean = x_table_excel[n]
        y_mean = y_table_excel[n]
        z_mean = z_table_excel[n]

# last value is lost it's temporary fix
objectid_table.append(x)
h_table.append(round(h_mean / counter, 3))
x_table.append(round(x_mean / counter, 3))
y_table.append(round(y_mean / counter, 3))
z_table.append(round(z_mean / counter, 3))

for k in range(len(wb["OBJECTID_1"])):
    n = wb["OBJECTID_1"][k]

    if n not in duplicate_dict:
        duplicate_dict[n] = True

        xp_table.append(wb["Xp"].iloc[k])
        yp_table.append(wb["Yp"].iloc[k])
        g_table.append(wb["g"].iloc[k])
        hp_table.append(wb["H"].iloc[k])

for i in range(len(objectid_table)):
    dic = {}

    dic["ID"] = objectid_table[i]
    dic["Xp"] = yp_table[i]
    dic["Yp"] = xp_table[i]
    dic["Hp"] = hp_table[i]
    dic["g"] = g_table[i]
    dic["X"] = y_table[i]
    dic["Y"] = x_table[i]
    dic["Hnorm"] = h_table[i]
    dic["Z"] = z_table[i]

    data.append(dic)

#print(data)
#print(len(data))

df = pd.DataFrame(data)

pi = math.pi
k = 6.67508*(10**-11)
p = 2.67
r = 1200
p_1 = []

for i in range (len(df)):
    eq_1 = 2*pi*k*p*(df["Hp"][i]-df["Hnorm"][i])
    p_1.append(eq_1)

grouped_data = {}

for i in range(len(wb["OBJECTID_1"])):
    object_n = wb["OBJECTID_1"][i]
    x = wb["Y"][i]
    y = wb["X"][i]
    H = wb["Hnorm"][i]
    xp = wb["Yp"][i]
    yp = wb["Xp"][i]
    Hp = wb["H"][i]

    if object_n not in grouped_data:
        grouped_data[object_n] = {
            "x_values": [],
            "y_values": [],
            "H_values": [],
            "xp_values": [],
            "yp_values": [],
            "Hp_values": [],
        }

    grouped_data[object_n]["x_values"].append(x)
    grouped_data[object_n]["y_values"].append(y)
    grouped_data[object_n]["H_values"].append(H)
    grouped_data[object_n]["xp_values"].append(xp)
    grouped_data[object_n]["yp_values"].append(yp)
    grouped_data[object_n]["Hp_values"].append(Hp)

TCR_results = []

for object_n, data in grouped_data.items():
    x_values = data["x_values"]
    y_values = data["y_values"]
    H_values = data["H_values"]
    xp_values = data["xp_values"]
    yp_values = data["yp_values"]
    Hp_values = data["Hp_values"]

    eq_values = []
    for j in range(len(x_values) - 1):
        x = x_values[j]
        y = y_values[j]
        H = H_values[j]
        xp = xp_values[j]
        yp = yp_values[j]
        Hp = Hp_values[j]

        eq = (x * math.log(y + r) + y * math.log(x + r) - H * math.atan(x * y / (H * r))) - (
                    xp * math.log(yp + r) + yp * math.log(xp + r) - Hp * math.atan(xp * yp / (Hp * r)))
        TCR = k * p * eq
        eq_values.append(TCR)

    TCR_results.append(np.sum(eq_values))

TCR = []

for k in range(len(TCR_results)):

    TCR.append(p_1[k]-TCR_results[k])

df.insert(9, 'TCR', TCR)
df.to_excel("points_data.xlsx", index=False)
df.to_csv("points_data.csv", index=False)