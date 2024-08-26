import json
from pathlib import Path
import random
import os, gc

import tensorflow.keras as keras
import tensorflow as tf

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import market_stats as mstat

from memory_profiler import profile

#utils, will review later
def check_month_difference(arr, dic, publish_date):
	good_dates = {}
	ret = False

	publish_date = ((int(publish_date[:4])-1)*365 ) + ((int(publish_date[4:6])-1)*30)+(int(publish_date[6:8]))

	for i in arr:
		if not i.isnumeric() or len(i) != 8:
			good_dates[i] = dic[i]
			continue

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

def while_less(data, times, target_time):
	
	closest_less = -1
	for i in range(len(times)):
		if isinstance(i, int):
			z = i
		else:
			z = int(float(times[i]))

		if target_time >= z and z > closest_less:
			closest_less = i
	
	if closest_less != -1:
		return data[i]
	else:
		return np.nan	

def dict_to_arr(data, competitor):
	last_arr = ""
	roc_arr = {}

	for date in data["stock_price"].keys():
		data_at_utc = {}
		line = data["stock_price"][date]

		dat = int(float(date))

		for i in line.keys():
			data_at_utc[i] = float(line[i])

		if competitor == False:
			#print(company["competitors"].keys())
			for g in data["competitors"].keys():
				comper = data["competitors"][g]
				#print(comper.keys())
				if dat in list(comper.keys()):
					#print(comper[int(dat)])
					citer = 0
					for ccat in comper[int(dat)]:
						if(ccat == 0.0):data_at_utc[g+"_"+str(citer)] = ccat
						else:data_at_utc[g+"_"+str(citer)] = comper[int(dat)][ccat]

						citer+=1

			try:
				for mfactor in data["macros"]["macro_factors"].keys():
					if dat in data["macros"]["macro_factors"][mfactor]["time"]:
						data_at_utc["macros_"+mfactor] = (float(data["macros"]["macro_factors"][mfactor]["value"][data["macros"]["macro_factors"][mfactor]["time"].index(dat)]))
					else:
						d = while_less(data["macros"]["macro_factors"][mfactor]["value"],data["macros"]["macro_factors"][mfactor]["time"],dat)
						if isinstance(d, float):continue
						if d.find("None") == -1:data_at_utc["macros_"+mfactor] = (float(d))
						else:data_at_utc["macros_"+mfactor] =np.nan

				for control in ["gold", "oil", "crypto"]:#gold:low-high, oil:high-low[flipped], crypto:low-high
					for subcontrol in data["macros"][control].keys():
						subc = data["macros"][control][subcontrol]
						dp = while_less(subc["price"], subc["time"], dat)
						
						if str(dp).find("None") == -1:
							data_at_utc[control+":"+subcontrol] = float(dp)
						else:
							data_at_utc[control+":"+subcontrol] = np.nan
			
			except KeyError:
				pass#pass, not present if competitor

			'''
			fdates = []
			for filing in data["statisticalData"]:#high low
				fdates.append(int(float(mstat.convert_time(filing["filingDate"]))))

			second_iter = 0
			try:
				while fdates[second_iter] > dat:
					second_iter+=1

				quarterly = data["statisticalData"][second_iter]
				if "scale" in quarterly.keys():
					scale = quarterly["scale"]
				else:
					scale = ""
					
				if scale == "million":
					scale = 1000000
				elif scale == "thousand":
					scale = 1000
				else:
					scale=1
					pass#when scale == ''

				third_iter = 0
				kkey = ""
				kkeys = []

				for key in quarterly.keys():
					if key in ["method", "scale", "url", "filingDate"]:continue
						#take into account there should be assumed two and fill with nans if not
					third_iter+=1
					kkey = key
					kkeys = list(quarterly[key].keys())

					for k in kkeys:
						try:
							if quarterly[key][k].isnumeric():data_at_utc[key+":"+k] = float(int(quarterly[key][k])*scale)
						except AttributeError:
							data_at_utc[key+":"+k] = float((quarterly[key][k])*scale)

				if third_iter < 3:
					if "6 months" not in data_at_utc.keys():
						for k in kkeys:
							data_at_utc["6 months:"+k] = np.nan
					elif "3 months" not in data_at_utc.keys():
						for k in kkeys:
							data_at_utc["3 months:"+k] = np.nan
					elif "12 months" not in data_at_utc.keys():
						for k in kkeys:
							data_at_utc["12 months:"+k] = np.nan
					else:
						print("what??")

			except IndexError as e:
				pass
				#print(str(e))
				#print(dat)
				#print(fdates)
			'''
		for vol in ["10", "100", "365"]:#low to high
			#print(data["vol"+vol]["time"])
			#print(dat)
			pdat = data["vol"+vol]
			if isinstance(pdat, list):#weird error I thought I repaired
				break

			try:
				data_at_utc["vol"+vol] = pdat["price"][pdat["time"].index(dat)]
			except ValueError:
				data_at_utc["vol"+vol] = while_less(pdat["price"], pdat["time"], dat)


		for ama in ["10", "100", "365"]:#low to high
			pdat = data["ama"+ama]
			try:
				data_at_utc["ama"+ama] = pdat["price"][pdat["time"].index(dat)]
			except ValueError:
				data_at_utc["ama"+ama] = while_less(pdat["price"], pdat["time"], dat)
		
		roc_arr[int(dat)] = data_at_utc

	gc.collect()
	return roc_arr

#model processing, modding, and dumping results
def model_evolution(models, seeds, results, factors):#magic happens here
	new_mods = []
	facts = []

	facts.append(factors)
	if len(models) == 0:

		for seed in seeds:
			biases = False
			layer_len = factors		
			mod = keras.Sequential()
			mod.add(keras.layers.Dense(factors))
			output_layer = keras.layers.Dense(1, activation="linear")

			s = seed.split(",")
			for cat in range(len(s)):
				category = s[cat]
				if cat == 2:
					if int(category) == 2:
						biases = True
					else:
						layer_len += int(s[cat])
			facts.append(layer_len)
			mod.add(keras.layers.Dense(layer_len*1.25,activation="sigmoid",use_bias=biases))
			mod.add(output_layer)
			new_mods.append(mod)

	elif len(models) == 1:
		
		output_layer = keras.layers.Dense(1, activation="linear")
		hidden_len = models[0].get_layer(index=1).units

		for seed in seeds:
			biases = False
			mod = keras.Sequential()
			mod.add(keras.layers.Dense(models[0].get_layer(index=0).units))

			s = seed.split(",")
			for cat in range(len(s)):
				category = s[cat]
				if cat == 1:
					if int(category) == 1:
						biases = True
					else:
						hidden_len += int(s[cat])
			
			facts.append(hidden_len)
			mod.add(keras.layers.Dense(hidden_len,activation='sigmoid',use_bias=biases))
			mod.add(output_layer)
			new_mods.append(mod)

	else:
		top_two = []
		results_two = []

		for model in range(len(models)):

			if len(top_two) < 2:
				top_two.append(models[model])
				results_two.append(results[model])
			else:
				if results_two[0] > results[model]:
					top_two[0] = (models[model])
					results_two[0] = (results[model])
				elif results_two[1] > results[model]:
					top_two[1] = (models[model])
					results_two[1] = (results[model])
				else:
					pass
		
		ret1, ret2 = model_evolution([top_two[0]], seeds[:5], results_two[0], factors[0])
		ret12, ret22 = model_evolution([top_two[1]], seeds[5:], results_two[1], factors[0])
		gc.collect()
		return ret1+ret12, ret2+ret22

	gc.collect()
	return new_mods, facts

def gen_seed_func(all_factors):
	'''
	add hidden layer nodes/sub hidden layer nodes#how would this actually effect the model
	for layers add a bias
	'''

	return [math.ceil(all_factors*(4/3)), 1]

def gen_seed(possiblities_of_change, lengthb):
	seeds = []
	for seed in range(lengthb):
		s = ""
		ite = 0
		for i in possiblities_of_change:
			if ite == 0:
				if random.randrange(0,i,1) > .5:
					s+=str(1)
				else:
					s+=str(-1)
			else:
				s+=str(random.choice([0,1]))

		seeds.append(s)

	return seeds

def model_graph_generator(model_history, company_name):
	plt.clf()
	plt.semilogy(range(len(model_history)),model_history)
	plt.savefig("./figs/"+company_name.replace(" ", "_").replace(".", "")+".png")
	plt.clf()#maybe try plt.close()
	#less then 10^2, linear instead of log
	'''
	plt.plot(range(len(model_history)),model_history)
	plt.ylim([0,2])
	plt.savefig("./figs/removed_outliers_"+company_name.replace(" ", "_").replace(".", "")+".png")
	'''

def accuracy_graph(x, x2, company_name):
	plt.clf()
	plt.plot(x, label="expected")
	plt.plot(x2, label="predicted")
	plt.legend()
	plt.savefig("./figs/accuracy_"+company_name.replace(" ", "_").replace(".", "").replace(",", "")+".png")

#data processing/prep
def remove_uncommon_categories(company):
	category_math = {}

	for i in company["statisticalData"]:
		for j in i.keys():
			if j in ["method", "scale", "url", "filingDate"]:
				continue
			for key in i[j].keys():
				if key in category_math.keys():
					category_math[key]+=1
				else:
					category_math[key] = 1
	pops = 0
	non = 0

	for category in category_math.keys():
		if category_math[category] < len(company["statisticalData"])/2:
			category_math[category] = False
			pops+=1
		else:
			category_math[category] = True
			non+=1

	for i in company["statisticalData"]:
		for j in i.keys():
			if j in ["method", "scale", "url", "filingDate"]:
				continue

			bist = list(i[j].keys())
			for key in bist:
				if category_math[key] == False:
					del i[j][key]

	print("bad: "+str(pops)+" good: "+str(non))
	gc.collect()
	return company

def all_nn_ready():
	total_p1 = 0
	second_pass = 0
	third_test = 0

	passed = []

	for j in Path("./stocks/").iterdir():
		if str(j).find(".json") == -1:continue
		try:
			with open("./"+str(j),"r") as f:
				company = json.load(f)
				bad = 0
				
				for i in company["statisticalData"]:
					if len(i.keys()) < 4:bad+=1

				
				if bad/len(company["statisticalData"]) > 0.3:
					print("skipping: "+str(company["name"]))

				else:
					total_p1+=1
					#print("exploring further: "+str(company["name"])+" testing total categories per date")

					avg_len = 0
					total = 0
					ite = 0
					temparr = []
					
					for i in reversed(company["statisticalData"]):#find just the two keys you need, start at the bottom to find first file add 3 months
						
						ite+=1
						total += 1

						mod_i = check_month_difference(i.keys(), i, mstat.just_alpha(i["filingDate"]))
						avg_len += len(list(mod_i.keys()))	
						temparr.append(mod_i)
							
					if avg_len/total >= 1.5:
						company["statisticalData"] = temparr[::-1]
						second_pass+=1
						#print(str(company["name"])+" passed test 2 with: "+str(avg_len/total))

						avg_cats = 0
						div = 0

						for stat in company["statisticalData"]:
							for cat in stat.keys():
								if cat not in ["method", "scale", "url", "filingDate"]:
									avg_cats += len((stat[cat]).keys())
									div+=1

						if avg_cats/div > 10:
							passed.append(company)
							third_test+=1
		except json.decoder.JSONDecodeError:
			continue

	print(str(total_p1)+"/100 original companies( > 70%)")
	print("of these, have enough dates( > 1.5) "+str(second_pass))
	print("Of these " + str(third_test)+ " have enough average categories ( > 10)")
	#print(str(passed))
	gc.collect()
	return passed

@profile
def main_wrapper(macro_economic_factors, comp):
	model_history = []

	print("starting: "+comp["name"])
	company = remove_uncommon_categories(comp)
	company["competitors"] = {}
	results = []

	num = 0
	for i in Path("./competitors/").iterdir():
		pi = str(i).split("/")[1]
		if pi.find(comp["sic"]) == 0:
			filefile = open("./"+str(i), "r")
			
			l = ""
			lines = filefile.readlines()
			for t in lines:
				l += t
			l = json.loads(l)

			cik = (str(filefile).split("-")[1])
			print("Finding competitor: "+str(cik[:cik.find(".")]))
			company["competitors"][cik[:cik.find(".")]] = dict_to_arr(remove_uncommon_categories(l), True)
			del l
			filefile.close()
			num+=1
			gc.collect()
			#if num == 6:break

	print("Loaded competitors")
	company["macros"] = macro_economic_factors

	pdata = pd.DataFrame(dict_to_arr(company, False)).T
	outputdata = []

	ite = 0#what is this?
	length = len(list(pdata.iterrows()))-1
	print("length of input data: "+str(length))
	for r in pdata.index:
		if ite != 0:
			outputdata.append(pdata.loc[r]["Open"])
		
		ite+=1
	
	inputdata = pd.DataFrame(pdata).dropna(axis=1, how="any")[:-1]
	outputdata = pd.DataFrame(outputdata)

	ishape = str(inputdata.shape)
	cols = int(str(ishape.split(",")[1]).replace(")", "").replace(" ", ""))
	print(cols)

	if cols == 0:
		print("skipping: "+company["name"])
		return
	'''elif cols <= 20:#arbitrary
		inputdata = pd.DataFrame(pdata).dropna(axis=0, how="any")[:-1]
		#try 10% if that doesn't work too
	else:
		pass'''

	inputdata.to_csv("./input_data/test_"+company["name"].replace(".", "").replace(",", "").replace(" ", "_")+".csv")
	ishape = str(inputdata.shape)

	print(ishape)
	print(str(outputdata.shape))
	
	model = keras.Sequential()
	input_layer = keras.layers.Dense(cols)
	hidden_layer = keras.layers.Dense(
		math.ceil((cols)*(1.25)),
		activation="sigmoid",
		use_bias=False)
	output_layer = keras.layers.Dense(1, activation="linear")
	model.add(input_layer)
	model.add(hidden_layer)
	model.add(output_layer)
	
	callb = [
		keras.callbacks.ModelCheckpoint("./models/"+mstat.just_alpha(company["name"])+("/{mean_squared_error:.2f}.keras"), monitor="mean_squared_error")#batch was removed for now
	]
	
	model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mean_squared_error"])
	#what?????????????	
	h = model.fit(x=inputdata, y=outputdata, validation_split=0.1, epochs=50, callbacks=callb, verbose=0)#maybe config batchsize
	results.append(h.history["mean_squared_error"])
	model_history.append(h.history["mean_squared_error"])#plotting model.history.history gives loss and mse 
	accuracy_graph(outputdata, model.predict(inputdata), company["name"])
	models = []
	fs = []
	seeds = gen_seed(gen_seed_func(cols), 10)#model_evolution hardcoded to split list by 5
	print(":::::::::::)Starting Mutation of Network")
	for i in range(10):
		if i == 0:
			models, fs = model_evolution(models, seeds, results, cols)
		else:
			models, fs = model_evolution(models, seeds, results, fs)
		
		seeds = gen_seed(gen_seed_func(cols), 10)
		results = []
		for mod in models:
			model.compile(optimizer="adam",loss="mean_squared_error", metrics=["mean_squared_error"])
			h = model.fit(x=inputdata, y=outputdata, validation_split=0.1, epochs=50, callbacks=callb, verbose=0)
			model_history.append(h.history["mean_squared_error"])
			results.append(h.history["mean_squared_error"])

	print("plotting the results")
	model_graph_generator(model_history, company["name"])

	del inputdata, outputdata, company, pdata, models, model, results, h, fs, seeds, ishape, model_history
	gc.collect()

try:
	os.mkdir("./input_data")
except Exception:
	for i in Path("./input_data").iterdir():
		i.unlink()

for i in Path("./competitors").iterdir():#remove empty competitors
	if len(i.open("r").read()) < 30:
		i.unlink()

try:
	os.mkdir("./models")
except Exception:
	for i in Path("./models").iterdir():
		lowest = 1000
		for j in i.iterdir():
			if lowest < float(str(j).replace(".keras", "").split("/")[2]):
				lowest = float(str(j).replace(".keras", "").split("/")[2])
			else:
				j.unlink()

		for j in i.iterdir():
			if str(j).find(str(lowest)) == -1:
				j.unlink()

try:
	os.mkdir("./figs")
except Exception:
	for i in Path("./figs").iterdir():
		i.unlink()

macro_economic_factors = {"macro_factors" : {}, "oil":{}, "crypto":{}, "gold":{}}
with open("macro_economic_factors.json", "r") as f:
	fs = ["fed_interest_rate","unemploymentRate", "CPIUrban", "PPICommodities"]
	for ggg in fs:
		macro_economic_factors["macro_factors"][ggg] = {"time":[], "value":[]}
	
	lines = json.loads(f.read())
	
	for l in lines.keys():
		for i in fs:
			if i in lines[l].keys():
				macro_economic_factors["macro_factors"][i]["time"].append(l)
				macro_economic_factors["macro_factors"][i]["value"].append(lines[l][i])

for gold in Path("./gold/").iterdir():
	with open(str(gold), "r") as g:
		macro_economic_factors["gold"][str(gold)] = {"time":[],"price":[]}
		for line in readlines(g):
			jline = line.split(":")
			macro_economic_factors["gold"][str(gold)]["time"].append(int(float(jline[0])))
			macro_economic_factors["gold"][str(gold)]["price"].append(jline[1])

for crude in Path("./crude_oil/").iterdir():
	macro_economic_factors['oil'][str(crude)] = {"time":[],"price":[]}
	for line in readlines(crude.open())[::-1]:#flipped so works?
		jline = line.split(":")

		macro_economic_factors['oil'][str(crude)]["time"].append(int(float(mstat.convert_time(jline[0]))))
		macro_economic_factors['oil'][str(crude)]["price"].append(jline[1][:jline[1].rfind(".")])

for crypto in Path("./crypto/").iterdir():
	macro_economic_factors["crypto"][str(crypto)] = {"time":[],"price":[]}
	for line in readlines(crypto.open()):
		colon = line.split(":")
		macro_economic_factors["crypto"][str(crypto)]["time"].append(int(colon[0]))
		macro_economic_factors["crypto"][str(crypto)]["price"].append(colon[1])

#so this var will be needed for network gen
gc.enable()
for comp in all_nn_ready():	
	main_wrapper(macro_economic_factors, comp)
	gc.collect()

#structure: inp-sigmoid-linear is the best thus far[test layer mutation, adding H layers]
#-record on this structure: 7 mse
