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


# import Excel 
df = pd.read_excel('raw_data_cleaned.xlsx')
unique = unikalne_w_kolejnosci(df)

groupped_data = grupping(df)

TCR_result, h_diff_table = TCR(groupped_data)


df2 = []


df2 = pd.DataFrame(unique)

df2.insert(1, 'TCR',TCR_result)  
df2.insert(2,'Hnorm',groupped_data["Hp"])  
df2.insert(3,'Height_diff',h_diff_table)  
df2.to_excel("dane_graw_tcr_v2.xlsx", index=False)  
df2.to_csv("dane_graw_tcr_v2.csv", index=False)  
