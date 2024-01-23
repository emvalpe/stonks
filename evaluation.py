import json
from pathlib import Path

def just_alpha(text, spaces=False):
	if type(text) == type(1):return text
	new_str = ""
	for i in range(len(text)):
		if text[i].isalnum():
			new_str += text[i]
		elif spaces and text[i] == " ":
			new_str += text[i]

	return new_str

def check_month_difference(arr, dic, publish_date):
	good_dates = {}
	ret = False

	publish_date = ((int(publish_date[:4])-1)*365 ) + ((int(publish_date[4:6])-1)*30)+(int(publish_date[6:8]))

	for i in arr:
		value = ((int(i[:4])-1)*365 ) + ((int(i[4:6])-1)*30)+(int(i[6:8]))		

		test = int(publish_date-value)

		if test >= 0.0 and test <= 130:
			good_dates["3 months"] = dic[i]
			publish_date = value
		elif test >= 150 and test <= 230:
			good_dates["6 months"] = dic[i]
		elif test >= 270 and test <= 370:
			good_dates["12 months"] = dic[i]
		else:
			if test > 0:
				pass
				'''
				print(test)
				print(str(publish_date)+"-"+str(value))
				'''

	return good_dates

def all_nn_ready():
	total_p1 = 0
	second_fail = 0
	third_test = 0

	passed = []

	for j in Path("./stocks/").iterdir():
		if str(j).find(".json") == -1:continue
		with open("./"+str(j),"r") as f:
			company = json.loads(f.read())
			lowest = 1+4#4 is lowest
			bad = 0
			
			for i in company["statisticalData"]:
				if len(i.keys()) < lowest:bad+=1

			
			if bad/len(company["statisticalData"]) > 0.3:
				print("skipping: "+str(company["name"]))

			else:
				total_p1+=1
				print("exploring further: "+str(company["name"])+" testing total categories per date")

				avg_len = 0
				total = 0
				ite = 0
				
				for i in reversed(company["statisticalData"]):#find just the two keys you need, start at the bottom to find first file add 3 months
					ite+=1
					if len(i.keys())-4 == 0:
						total+=1
						continue

					keys = list(i.keys())

					if keys:
						keys.remove("method")
						keys.remove("filingDate")
						keys.remove("url")
						keys.remove("scale")
					else:
						total+=1
						continue

					publish_date = just_alpha(i["filingDate"])

					mod_i = check_month_difference(keys, i, publish_date)
					
					avg_len += len(list(mod_i.keys()))		
					total+=1
					#change
					company["statisticalData"][len(company["statisticalData"])-ite] = mod_i
						
				if avg_len/total >= 1.5:
					second_fail+=1
					print(str(company["name"])+" passed test 2 with: "+str(avg_len/total))

				else:
					avg_cats = 0
					div = 0

					for stat in company["statisticalData"]:
						for cat in stat.keys():
							if cat not in ["method", "scale", "url", "filingDate"]:
								avg_cats += len((stat[cat]).keys())
								div+=1

					if avg_cats/div > 10:
						print(str(company["name"])+" passed test 3 with: "+str(avg_cats/div))
						passed.append(company)
						third_test+=1


	print(str(total_p1)+"/100 original companies( > 70%) ")
	print("of these, have enough dates( > 1.5) "+str(second_fail))
	print("Of these " + str(third_test)+ " have enough average categories ( > 10)")
	print(str(passed))

	return passed


for company in all_nn_ready():
	
