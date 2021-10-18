import pandas as pd
import numpy as np
import csv

cdli = pd.read_csv('MET_cdli.csv', encoding = "ISO-8859-1")
print(cdli)
met = pd.read_csv('MET_data.csv') 
met["accessionYear"] = 0
print(met)


a = np.intersect1d(cdli.columns, met.columns)
print(a)