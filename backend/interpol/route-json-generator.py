import json
import pandas as pd

def csv_to_json(csv_data):
    df = pd.read_csv(csv_data)
    json_list = []
    for index, row in df.iterrows():    
        entry = {"MODAL": row.MODAL, "SPOT1": int(row.SPOT1), "SPOT2": int(row.SPOT2)}
        json_list.append(entry)

    with open("routes.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(json_list, indent=2))

    return json.dumps(json_list, indent=2) 
    

csv_data = """MODAL,SPOT1,SPOT2
BUS,100,82
BUS,102,67
HIDDEN,194,157
METRO,111,67
METRO,128,89
TAXI,114,113
TAXI,115,102
TAXI,115,114
TAXI,116,104"""



json_output = csv_to_json("routes.csv")
print(json_output)