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

# mathematical formula #3
def full_bouger_anomaly_gravity(delta_gt, delta_gh, p, h):
    return delta_gt + delta_gh + (0.04187 * p * h)

# mathematical formula #4
def normal_gravity(fi):
    return 978032.67715 * (1 + 0.00530244 * math.sin(fi)**2 - 0.0000058495 * math.sin(2 * fi)**2) #[mGal] B => fi

# import excel file with our data from buffers
wb = pd.read_excel('raw_data_cleaned.xlsx')

# variables to group data with id's of objects
bufor_point = []
index_table = wb["OBJECTID_1"]
h_table_excel = wb["Hnorm"]
x_table_excel = wb["X"]
y_table_excel = wb["Y"]
z_table_excel = wb["Z"]
# additional
g_table_excel = wb["g"]
h_normal_table_excel = wb["H"]



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

# additional
delta_gh = []
go_prim = []
delta_go_prim = []
gamma0 = []
delta_gB = []
p = 0.2670 # average density of the topographic mass
g0e = []
delta_g0e = []

# mathematical formula #4
for n in range(len(wb)):
    gamma0.append(normal_gravity(wb["B"][n]))

# mathematical formula #1.1
for n in range(len(wb)):
    delta_gh.append(freeair_anomaly(wb["H"][n]))

# mathematical formula #1.2
for n in range(len(wb)):
    go_prim.append(gravity_intensity(wb["g"][n],delta_gh[n]))

# mathematical formula #1.3
for n in range(len(wb)):
    delta_go_prim.append(gravity_intensity(go_prim[n],gamma0[n]))

# mathematical formula #2.1
for n in range(len(wb)):
    delta_gB.append(bouger_anomaly_gf(delta_gh[n], p, wb["H"][n]))

# mathematical formula #2.2
for n in range(len(wb)):
    g0e.append(gravity_value_bouger_anomaly_gf(wb["g"][n], delta_gB[n]))

# mathematical formula #2.3
for n in range(len(wb)):
    delta_g0e.append(incomplete_gravity_value_bouger_anomaly_gf(g0e[n], gamma0[n]))

# create tables with means for object id's
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
# last value is lost, so it's temporary fix of our algorithm
objectid_table.append(x)
h_table.append(round(h_mean / counter, 3))
x_table.append(round(x_mean / counter, 3))
y_table.append(round(y_mean / counter, 3))
z_table.append(round(z_mean / counter, 3))

# read and grouping known values from gravimetry points
for k in range(len(wb["OBJECTID_1"])):
    n = wb["OBJECTID_1"][k]

    if n not in duplicate_dict:
        duplicate_dict[n] = True

        xp_table.append(wb["Xp"].iloc[k])
        yp_table.append(wb["Yp"].iloc[k])
        g_table.append(wb["g"].iloc[k])
        hp_table.append(wb["H"].iloc[k])

# joining all data in one table
for i in range(len(objectid_table)):
    dic = {"ID": objectid_table[i], 
            "Xp": yp_table[i], 
            "Yp": xp_table[i],
            "Hp": hp_table[i], 
            "g": g_table[i],
            "X": y_table[i], 
            "Y": x_table[i], 
            "Hnorm": h_table[i], 
            "Z": z_table[i]}

    data.append(dic)

df = pd.DataFrame(data) # dataframe with data needed to do TCR equations
pi = math.pi
k = 6.67508 * (10 ** -11) # Newton gravitonal consant
p = 2670 # average density of the topographic mass

grouped_data = {}

# another way to group our data
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
# TCR equation loop
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
        r = math.sqrt((x - xp) ** 2 + (y - yp) ** 2 + (H - Hp) ** 2) 
        #spherical geocentric radius
        # integration over three variables
        eq = (xp * math.log(yp + r) + yp * math.log(xp + r) 
              - ((Hp * math.atan(xp * yp / (Hp * r))) 
                - (x * math.log(y + r) + y * math.log(x + r)
                - H * math.atan(x * y / (H * r)))))
        
        TCR = (k * p * eq) / 100000 # TCR calculation
        eq_values.append(TCR)
    TCR_results.append(np.sum(eq_values)) # Sum of single equations

df.insert(9, 'TCR', TCR_results) # Adding TCR to our dataframe
df.to_excel("points_data.xlsx", index=False) # Exporting data to excel
df.to_csv("points_data.csv", index=False)


#p = 0.2670 # average density of the topographic mass
#print(df["TCR"])
# mathematical formula #3
#for n in range(len(wb)):
    #delta_g0e.append(full_bouger_anomaly_gravity(TCR_results[n], delta_gh[n], p, wb["H"][n]))