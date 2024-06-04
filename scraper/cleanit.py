import json
import pandas as pd

all_data = []
all_data_read = {}
with open("./data.json", "r") as f:
    all_data_read = json.loads(f.read())
for e in all_data_read["schemas"]:
    all_data.append(e)
print(f"Found {len(all_data)} entries of data")
df = pd.DataFrame(all_data)
print(len(df.index), df.columns)
print(f"Duplicates: {df[df.duplicated(keep=False)]}")
