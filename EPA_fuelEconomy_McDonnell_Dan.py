# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 11:30:00 2020

@author: Dan McDonnell
"""

## Data source: https://www.fueleconomy.gov/feg/download.shtml
## Using 2020 "EPA Green Vehicle Guide XLSX"

## https://www.fueleconomy.gov/feg/EPAGreenGuide/xls/all_alpha_20.xlsx

## This script retrieves fuel economy data from the US Department of Energy for all car models sold domestically in the United States.
## Applies corrections to text, parses car brand names, groups data by brand name. 
## Presents and visualizes descriptive statistics of which car brands produce the most fuel efficient, or least polluting vehicles
## Using most recently available 2020 data

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# from bokeh.plotting import figure, output_file, show

# import seaborn
fuel = pd.read_excel('https://www.fueleconomy.gov/feg/EPAGreenGuide/xls/all_alpha_20.xlsx')
## Temporarily commented out while using local copy of data file

# fuel = pd.read_excel(r'C:\Users\Dan McDonnell\Desktop\all_alpha_20.xlsx') ##Local working copy, comment out when done.
fuel.sort_index(inplace = True) #Sort by auto-generated index to keep everything in order for now and preserve original sort of source data.

# Print some basic info about the dataset
# print(fuel.dtypes)
# print(fuel.info)

# Copy the "Model" column and alter some OEM names with spaces so that the space character is replaced with a hyphen

fuel["ModelModified"] = fuel["Model"]

fuel["ModelModified"] = fuel["ModelModified"].str.replace("ASTON MARTIN", "ASTON-MARTIN")
fuel["ModelModified"] = fuel["ModelModified"].str.replace("ALFA ROMEO", "ALFA-ROMEO")
fuel["ModelModified"] = fuel["ModelModified"].str.replace("LAND ROVER", "LAND-ROVER")

##Parse OEM brand names and product names off of model names and put them in their own column

fuel["BrandName"] = fuel["ModelModified"].str.split(" ").str.get(0)
fuel["CarName"] = fuel["ModelModified"].str.split(" ", n = 4).str.get(1)
#fuel["TrimInfo"] = fuel["ModelModified"].str.split(" ").str.get(2)+=.str.get(3) #Get remainder of the ModelModified string (still working on)

# There doesn't appear to be an explicit unique ID for car models on this dataset. 
# I created one myself by conacatenating "Underhood_ID" with "Drive" (2wd/4wd/awd) 
# This gives me a good idea of a specific model regardless of trim package/body style

fuel["ModelID"] = fuel["Underhood ID"]+fuel["Drive"]

# Copy combined mpg column before converting to int. Need to deal with "Gas/Electric" format for hybrid cars before converting to int

fuel["HybridGasCombMPG_int"] = fuel["Cmb MPG"].str.split("/").str.get(0)
fuel["HybridElectricCombMPG_int"] = fuel["Cmb MPG"].str.split("/").str.get(1)
fuel.dropna(subset = ["HybridGasCombMPG_int","HybridElectricCombMPG_int"])

fuel["HybridGasCombMPG_int"] = fuel["HybridGasCombMPG_int"].fillna(0)
fuel["HybridElectricCombMPG_int"] = fuel["HybridElectricCombMPG_int"].fillna(0)

fuel["HybridGasCombMPG_int"] = fuel["HybridGasCombMPG_int"].astype(int)
fuel["HybridElectricCombMPG_int"] = fuel["HybridElectricCombMPG_int"].astype(int)

fuel["TotalCombMPG_int"] = np.nan
fuel["TotalCombMPG_int"] = (fuel["HybridGasCombMPG_int"]).where(fuel["HybridElectricCombMPG_int"] == 0)

# Naive assumption that hybrid cars true average mpg is somewhere between their GasMPG and ElectricMPG. 
# Averaging the two assumes an equal mix of gas and electric driving.
# It's a fair point that this could exagerate the efficency of some hybrids, for the sake of simplicity and demonstrating PANDAS an avergae keeps things straightforward 

fuel["TotalCombMPG_int"] = fuel["TotalCombMPG_int"].fillna((fuel["HybridGasCombMPG_int"] + fuel["HybridElectricCombMPG_int"])/2) 

# Data appears to be duplicated by Federal and California measurments so at this point I split the data into two dataframes while retaining the original.
fuel["Standard"] = fuel["Stnd Description"].str.split(" ").str.get(0) # More readable way to eyeball the two measurement standards

fuelCA = fuel.where(fuel["Cert Region"] == "CA")
fuelCA.dropna(how = "all", inplace = True)
fuelFED = fuel.where(fuel["Cert Region"] == "FA")
fuelFED.dropna(how = "all", inplace = True)

# From this point on I'll primarily using fuelFED for data investigation purposes

# Test aggregation with the pivot_table method 

fuelFED_Pivot1 = fuelFED.pivot_table(values = ["TotalCombMPG_int", "Greenhouse Gas Score", "Air Pollution Score"], index = "BrandName", aggfunc = "mean")

# PANDAS aggregation with the groupby method

vehicleType = fuelFED.groupby(["Veh Class","Drive"])
transmissionType = fuelFED.groupby(["Trans"])
brandOEM = fuelFED.groupby("BrandName")

vehicleTotals = vehicleType[["Air Pollution Score", "Greenhouse Gas Score", "TotalCombMPG_int"]].mean()
transmissionTotals = transmissionType[["Air Pollution Score", "Greenhouse Gas Score", "TotalCombMPG_int"]].mean()
brandTotals = brandOEM.agg({"Air Pollution Score" : "mean", "Greenhouse Gas Score" : "mean","TotalCombMPG_int" : "mean","ModelID" : "size"})
brandTotals.rename(columns = {"ModelID":"CountOfModels"})

#Visualization

plt.subplots_adjust(hspace = 0.8)
plt.tight_layout()
plt.style.use("ggplot")
plt.margins(0.8,0.8)

fuelEconChart = brandTotals.sort_values("TotalCombMPG_int", ascending = True).plot(
                kind = "barh",
                use_index = True,
                y = 'TotalCombMPG_int',
                align = 'center',
                width = 0.5,
                left = 4,
                fontsize = 4,
                color = 'blue'
                )

# plt.savefig("MPG_Chart.png", dpi = 800)


# plt.style.use("ggplot")
greenhouseChart = vehicleTotals.plot(
                kind = "barh",
                use_index = True,
                y = ['Greenhouse Gas Score', 'Air Pollution Score'],
                align = 'center',
                width = 0.5,
                left = 4,
                fontsize = 4 
                )
plt.savefig("Greenhouse_chart", dpi = 800)

# Another idea I wanted to develop but I couldn't figure out how to label the individual markers in the plot            
scatterChart = brandTotals.plot(kind = "scatter",
                use_index = True,
                x = 'Greenhouse Gas Score',
                y = 'Air Pollution Score',
                color = 'c',
                grid = True
                )























