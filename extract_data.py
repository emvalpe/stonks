import os
import json
from pathlib import Path

#chdir
p = Path("./submissions").iterdir()
desired_keys = ["cik", "entityType", "sic", "sicDescription", "name", "tickers", "exchanges", "ein", "description", "category", "stateOfIncorporation", "formerNames", "filings"]

try:
	os.remove("./submissions/placeholder.txt")
	os.remove("processed.json")
except Exception:
	pass

file_to_write = open("processed"+".json","w+")
for file in p:

	company = {}
	if file.is_file() == True and str(file.name).find("submissions") == -1:
		with open("./submissions/"+file.name, "r") as f:
			while True:
				line = f.readline()
				if not line:break
				try:
					read = json.loads(line)
				except json.decoder.JSONDecodeError:
					print("error at: " + file.name + " probably fine")#fix????
			
		for key in read.keys():
			if key in desired_keys:
				company[key] = read[key]

		if company != {} and company["entityType"].lower() == "operating":
			try:
				excess = company["filings"]["files"]
				if len(excess) != 0:
					for z in excess:
						filee = json.load(open("./submissions/"+z["name"],))
						for kem in company["filings"]["recent"].keys():
							company["filings"]["recent"][kem] = company["filings"]["recent"][kem] + filee[kem]
					
			except KeyError as e:
				print(e)

			company["acquired"] = []	
			file_to_write.write(json.dumps(company)+"\n")
		else:continue

file_to_write.close()
print("Completed Successfully")
