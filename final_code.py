import pandas as pd
import math
import numpy as np

def unikalne_w_kolejnosci(df):
    unikalne_wartosci = []  # Inicjalizujemy listę, w której przechowamy unikalne wartości w kolejności ich występowania

    for value in df["OBJECTID_1"]:
        if value not in unikalne_wartosci:  # Jeśli wartość nie znajduje się jeszcze w liście unikalnych wartości
            unikalne_wartosci.append(value)  # Dodaj ją do listy

    return unikalne_wartosci

def grupping(df):
    # variables
    indexes_data = df["OBJECTID_1"]
    hnorm_data = df["Hnorm"]
    hp_data = df["H"]

    # arrays
    objectids_table = []
    h_values_table = []
    hp_values_table = []
    n_of_pts_in_buff = []

    # indicators
    counter = 0
    hp = 0
    h_mean = 0
    objectid = 0
    n_of_pts = 0
    x = indexes_data[0]

    # create tables with grouped data for object id's
    for n in range(len(df["OBJECTID_1"])):
        # checks value for certain objectid
        if x == indexes_data[n]:
            # makes containers for mean calcs
            objectid += indexes_data[n]
            h_mean += hnorm_data[n]
            hp += hp_data[n]
            n_of_pts += 1
            # keeps track number of components
            counter += 1
        else:
            # calc mean or other values and append into value arrays
            objectids_table.append(objectid / counter)
            h_values_table.append(round(h_mean / counter, 6))  # mean height in each buffer
            hp_values_table.append(round(hp / counter, 6))  # height of each measure point
            n_of_pts_in_buff.append(n_of_pts)  # number of slices in each buffer

            # reset indicators
            counter = 1
            x = indexes_data[n]
            objectid = indexes_data[n]
            h_mean = hnorm_data[n]
            hp = hp_data[n]
            n_of_pts = 1

    # last value is lost, so it's temporary fix of our algorithm
    objectids_table.append(x)
    h_values_table.append(round(h_mean / counter, 6))
    hp_values_table.append(round(hp / counter, 6))
    n_of_pts_in_buff.append(n_of_pts)
    # data frame creation

    return pd.concat([pd.DataFrame(objectids_table, columns = ["OBJECTID"]),
                      pd.DataFrame(h_values_table, columns = ["H"]),
                      pd.DataFrame(hp_values_table, columns = ["Hp"]),
                      pd.DataFrame(n_of_pts_in_buff, columns = ["n_buffor"])], axis = 1)

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
def TCR(groupped_data):

    h_diff_table = []  # array to storage terrain height mean of each slice relative to measure point height
    TCR_result = []  # array to storage TCR final values
    k = 6.67508 * (10 ** -11)  # Newton gravitonal consant [m3/kg*s2]
    p = 2670  # average density of the topographic mass [kg/m3]
    r = 0  # the length of the initial radius limiting the slice [m]
    r2 = 1200  # the length of the final radius limiting the slice [m]
    pi = math.pi  # pi constant


    # TCR equation loop
    for i in range(len(groupped_data)):
        H = groupped_data["Hp"][i]  # H value of each point
        Hnorm = groupped_data["H"][i]  # Mean h value of terrain
        n = groupped_data["n_buffor"][i]  # Number of slices in buffer
        h_diff = abs(round(Hnorm - H,6))  # Difference between height of terrain and point
        h_diff_table.append(h_diff)  # Add diferrence to array

        # TCR - method for a cylinder
        eq = np.sum(r2 - r + math.sqrt(r**2 + h_diff**2) - math.sqrt(r2 ** 2 + h_diff ** 2))
        TCR = ((2/n)*pi*k*p * eq) * 10**5

        TCR_result.append(TCR)  # Adding TCRs to storage array

    return TCR_result, h_diff_table

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


unique = unikalne_w_kolejnosci(wb)

groupped_data = grupping(wb)

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
TCR_result, h_diff_table = TCR(groupped_data)

df.insert(13, 'TCR',TCR_result)  # Adding TCR to our dataframe

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

df.insert(17,'Hnorm',groupped_data["Hp"])  # Adding terrain mean to our dataframe
df.insert(18,'Height_diff',h_diff_table)  # Adding heights difference to dataframe


df.to_excel("points_data.xlsx", index=False) # Exporting data to excel
df.to_csv("points_data.csv", index=False)



print("All Done!")