import csv
import pandas as pd

filename = 'MET.csv'
data = pd.read_csv(filename, encoding = 'unicode_escape')
print(data)