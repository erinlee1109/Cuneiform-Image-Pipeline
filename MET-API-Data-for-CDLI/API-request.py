import requests
import json
import pandas as pd
from io import StringIO

def get_met_cuneiform():

	# retrieves object IDs with the keyword cuneiform 
	response = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search?q=cuneiform")

	# returns the response in dictionary
	object_id_dict = response.json()
	# print(object_id_dict)


	# isolate the list of object IDs
	object_id = object_id_dict["objectIDs"]
	# print(object_id)
	# print(len(object_id))

	json_output = []
	for i in range(670): # 670 because there are 670 outputs from MET as of Oct 17
		# create new url specific to the object ID
		object_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects/" + str(object_id[i])
		object_result = requests.get(object_url)
		json_output.append(object_result.json())

	# replace single quotes with double quotes
	json_output_clean = json.dumps(json_output)
	# print(json_output_clean)

	# StringIO provides file-like interface for strings. read_json throws error without it. 
	df=pd.read_json(StringIO(json_output_clean))

	# export result to new CSV file 
	df.to_csv('MET_data.csv')
	# print(df)

get_met_cuneiform()
