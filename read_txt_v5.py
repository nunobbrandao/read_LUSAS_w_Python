# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#Written by Nuno B Brandao on 27/02/2020
#The aim is to read several txt files from LUSAS, and compute the average forces at each node.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 
import glob

#list of files to be imported
files = glob.glob(os.path.join(os.getcwd(),"txt",'?-?.txt')) + glob.glob(os.path.join(os.getcwd(),"txt",'?-??.txt'))

#place each dataframe corresponding to each file (in files) to df_list
df_list = []
for i in files:
    #list with dataframes. Each data frame corresponds to a text file. 
    df = pd.read_csv(i, skiprows=92, sep='\t', lineterminator='\r',header=0)
    
    #Drop columns that are not necessary (column 0 so far). 
    df.drop(df.columns[0], axis = 1, inplace = True)
    
    #Drop numpy.nan values by row
    df.dropna(axis=0, inplace = True)
    
    #new column with the file name
    df["File"] = i.split("\\")[-1]
    
    #append df to df_master list
    df_list.append(df)

#concatenate DataFrame list in a global DataFrame
df_master = pd.concat(df_list)

#rename columns Y and X to Alpha and Radius (once coordinates in cylindrical coordinates)    
df_master.rename(columns={'Y':'Alpha','X':'Radius',}, inplace=True)

#Transform radial angle from -180 < Alpha < 180 to 0 < Alpha < 360 and round it to the 3rd fig
df_master.loc[:,'Alpha'] = (df_master.loc[:,'Alpha']+180).round(3)

df_master.to_excel("master.xlsx")

#df_example is a fraction of df_master and drop duplicated values in "Node" and "File" columns (keeping the 1st occorance)
df_example = df_master[#(df_master.loc[:, "Z"].between(-11,-8))&
                       (df_master.loc[:, 'Alpha'].between(85,95))&#|df_master.loc[:, 'Alpha'].between(0,1))&
                       ((df_master.loc[:, "File"]=="1-23.txt"))#|(df_master.loc[:, "File"]=="1-1.txt"))
                      ].drop_duplicates(subset = ["Node","File"], inplace = False)
              
#function returns the average of the chosen force
def Aver(df, Alpha, Z, alpha_range, depth_range, file_name,force_col_name):
    #df defines the original DataFrame from which the boolean mask is assessed
    #Alpha defines the alpha coordinate of a specific node 
    #Z defines the Z  coordinate of a specific node
    #mask_y defines the left and right range in cylindrical coordinates from which mean is calculated (in degrees)
    #mask_z defines the range up and down in Z direction from which mean is calculated (in m)
    #mask_file defines the *.txt name
    #force_col_name represents which force it's to be averaged
    alpha_bound_1 = (Alpha - alpha_range) % 360
    alpha_bound_2 = (Alpha + alpha_range) % 360
    if alpha_bound_1 < alpha_bound_2:
        mask_y = df.loc[:,'Alpha'].between(alpha_bound_1, alpha_bound_2)
    else:
        mask_y = (df.loc[:,'Alpha'] <= alpha_bound_2) | (df.loc[:,'Alpha'] >= alpha_bound_1)
    mask_z = df.loc[:, "Z"].between(Z - depth_range, Z + depth_range)
    mask_file = df.loc[:,"File"] == file_name
    return df.loc[(mask_z) & (mask_y) & (mask_file), force_col_name].mean()

#Wall thickness sets the depth and alpha range
depth_range = 1.2 

#function to define the alpha range
def alpha_range(depth_range, X):
    return depth_range*180/(np.pi*X)    

#cycle to go through each row with for
df_example = pd.concat(
        [df_example,
         df_example.apply(lambda row: Aver(df_master, row.loc['Alpha'],
                                           row.loc["Z"], 0, depth_range,
                                           row.loc["File"], ['Nt[kN/m]','Mt[kN.m/m]','St[kN/m]']
                                          ), axis=1).add_suffix('_a'),
                                           
        df_example.apply(lambda row: Aver(df_master, row.loc['Alpha'],
                                           row.loc["Z"], alpha_range(depth_range, row.loc['Radius']), 0,
                                           row.loc["File"], ['Nz[kN/m]','Mz[kN.m/m]','Sz[kN/m]']
                                          ), axis=1).add_suffix('_a'),
                                           
        df_example.apply(lambda row: Aver(df_master, row.loc['Alpha'],
                                           row.loc["Z"], alpha_range(depth_range, row.loc['Radius']), depth_range,
                                           row.loc["File"], ['Ntz[kN/m]','Mtz[kN.m/m]']
                                          ), axis=1).add_suffix('_a')                                  
   ], axis=1
)

##paste DataFrame in excel
#df_example.to_excel("df_example_v5.xlsx")
#
##plot marker='o',color='red'
fig, ax = plt.subplots()
df_example.plot(x="Nz[kN/m]", y="Z",marker='^',color='red', label='Absolute Value',linestyle='None',ax=ax)
df_example.plot(x="Nz[kN/m]_a", y="Z",marker='o',color='blue', label='Average Value',linestyle='None',ax=ax)
ax.legend()
#plt.plot(df_example["Nz[kN/m]_a"], df_example["Z"],marker='s',color='black',markerfacecolor='none',linestyle='None')
#axes = plt.gca()
#axes.set_xlim([-10000,-2200])
#axes.set_ylim([-70,-50])
#plt.show()