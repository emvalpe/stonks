import json
from pathlib import Path
import random
import os, gc
import time

import keras
from sklearn.model_selection import train_test_split

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import market_stats as mstat
import evolution as evol

from colorama import Fore, Back, Style
from memory_profiler import profile

import warnings 
warnings.filterwarnings("ignore")

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

def dict_to_arr(data, competitor=False):
	last_arr = ""
	roc_arr = {}

	for date in data["stock_price"].keys():
		data_at_utc = {}
		line = data["stock_price"][date]

		dat = int(float(date))

		for i in line.keys():
			data_at_utc[i] = float(line[i])

		if not competitor:
			#print(company["competitors"].keys())
			if 'competitors' in data.keys():
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
			
			for industry in data['macros']['industry-averages'].keys():
				if str(int(dat)) in list(data['macros']['industry-averages'][industry].keys()):
					for key in data['macros']['industry-averages'][industry][str(int(dat))].keys():
						data_at_utc[industry+':'+key] = data['macros']['industry-averages'][industry][str(int(dat))][key]

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
			if "vol"+vol in data.keys():
				pdat = data["vol"+vol]
			else:
				continue

			if isinstance(pdat, list):#weird error I thought I repaired
				break

			try:
				data_at_utc["vol"+vol] = pdat["price"][pdat["time"].index(dat)]
			except ValueError:
				data_at_utc["vol"+vol] = while_less(pdat["price"], pdat["time"], dat)


		for ama in ["10", "100", "365"]:#low to high
			if "ama"+ama in data.keys():
				pdat = data["ama"+ama]
			else:
				continue

			try:
				data_at_utc["ama"+ama] = pdat["price"][pdat["time"].index(dat)]
			except ValueError:
				data_at_utc["ama"+ama] = while_less(pdat["price"], pdat["time"], dat)
		
		roc_arr[int(dat)] = data_at_utc

	gc.collect()
	return roc_arr

#model results

def model_graph_generator(model_history, company_name):
	plt.clf()
	
	ite = 0
	for m in model_history:
		plt.plot(range(len(m)), m, label='model'+str(ite))
		ite+=1

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
	plt.savefig("./figs/first-model_accuracy_"+company_name.replace(" ", "_").replace(".", "").replace(",", "")+".png")

#data processing/prep
def remove_uncommon_categories(company):
	return company #ignoring for now will cycle back
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

def nn_ready(company):
	return True#skipping statisical data step for now
	try:
		bad = 0
						
		for i in company["statisticalData"]:
			if len(i.keys()) < 4:bad+=1

						
		if bad/len(company["statisticalData"]) > 0.3:
			#print("skipping: "+str(company["name"]))
			gc.collect()
			return False

		else:
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
					#print(str(company["name"])+" passed test 2 with: "+str(avg_len/total))

					avg_cats = 0
					div = 0

					for stat in company["statisticalData"]:
						for cat in stat.keys():
							if cat not in ["method", "scale", "url", "filingDate"]:
								avg_cats += len((stat[cat]).keys())
								div+=1

						if div and avg_cats/div > 10:
							gc.collect()
							return True

				else:
					gc.collect()
					return False

	except json.decoder.JSONDecodeError:
		gc.collect()
		return False

	gc.collect()
	return True

#@profile
def main_wrapper(macro_economic_factors, competitors, comp):

	print(Fore.GREEN + "starting: " + comp["name"] + " : " + comp["tickers"][0])
	company = comp #remove_uncommon_categories(comp)#temporary factor out
	
	if competitors != {}:
		company["competitors"] = competitors
		del company["competitors"][comp["ticker"][0]]

	company["macros"] = macro_economic_factors
	'''
	with open('passed_json-'+company["name"]+".json","w+") as d:
		d.write(json.dumps(company, indent=4))
		d.close()'''
		
	pdata = pd.DataFrame(dict_to_arr(company)).T##################################cause of issues
	outputdata = []

	ite = 0#what is this?
	length = len(list(pdata.iterrows()))-1
	#print("length of input data: "+str(length))
	for r in pdata.index:
		if ite != 0:
			outputdata.append(pdata.loc[r]["Open"])
		
		ite+=1
	
	inputdata = pd.DataFrame(pdata, columns=pdata.keys()).dropna(axis=1, how="any")[:-1]
	outputdata = pd.DataFrame(outputdata)

	xtrain, xtest, ytrain, ytest = train_test_split(inputdata, outputdata, test_sisze=.2)

	ishape = str(inputdata.shape)
	cols = int(str(ishape.split(",")[1]).replace(")", "").replace(" ", ""))
	print(Fore.BLUE + "length of passed categories " + str(cols))

	if cols == 0:
		print(Fore.RED+"skipping: "+company["name"])
		return
	'''elif cols <= 20:#arbitrary
		inputdata = pd.DataFrame(pdata).dropna(axis=0, how="any")[:-1]
		#try 10% if that doesn't work too
	else:
		pass'''

	inputdata.to_csv("./input_data/test_"+company["name"].replace(".", "").replace(",", "").replace(" ", "_")+".csv")
	ishape = str(inputdata.shape)

	#print(Fore.GREEN+ishape)
	#print(str(outputdata.shape))
	
	model = keras.Sequential()
	input_layer = keras.layers.Input((cols,))
	hidden_layer = keras.layers.Dense(
		math.ceil((cols)*(1.25)),
		activation="relu",
		use_bias=True)
	output_layer = keras.layers.Dense(1, activation="linear")#sigmoid because cross entropy based is better
	model.add(input_layer)
	model.add(hidden_layer)
	model.add(output_layer)
	
	callb = [
		keras.callbacks.ModelCheckpoint("./models/"+mstat.just_alpha(company["name"])+("/{mean_squared_error:.2f}.keras"), monitor="mean_squared_error")#batch was removed for now
	]
	
	model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mean_squared_error"])
	h = model.fit(x=xtrain.values, y=ytrain.values, validation_split=0.2, epochs=100, callbacks=callb, verbose=0, shuffle=True)#batch size = 1 for minimal memory alloc
	
	results = []
	model_history = []
	
	results.append(h.history["mean_squared_error"])#plotting model.history.history gives loss and mse 
	model_history.append({'shape':[cols, math.ceil((cols)*(1.25)), 1], 'remove_dp':[]})
	accuracy_graph(ytest.values, model.predict(xtest.values), company["name"])
	
	models = []
	print(Fore.MAGENTA+":::::::::::)Starting Mutation of Network")
	j = 1
	for i in range(10):
		#print(Fore.GREEN + str(len(model_history)))
		models = evol.new_model_evolution(model_history, results)

		for mod in list(models):
			#print(Fore.BLUE+"iter: "+str(i)+ " child: "+str(j))
			index = j
		
			t = pd.DataFrame()
			xt.pd.DataFrame()
			if len(model_history[index]['remove_dp']) > 0:
				print(Fore.BLUE+"1- shape: "+str(model_history[index]["remove_dp"]))
				for cat in xtrain:
					if list(xtrain.columns).index(cat) not in model_history[index]['remove_dp']:
						t[cat] = xtrain[cat]
						xt[cat] = xtest[cat]

			else:
				print(Fore.BLUE+"2- shape: "+str(cols))
				t = pd.DataFrame(xtrain)

			mod.compile(optimizer="adam",loss="mean_squared_error", metrics=["mean_squared_error"])
			h = mod.fit(batch_size=1, x=t.values, y=ytrain.values, validation_split=0.2, epochs=50, callbacks=callb, verbose=0, shuffle=True)#testing, set to 0 in prod
			
			accuracy_graph(ytest.values, mod.predict(xt.values), company["name"]+str(i)+str(j))
			results.append(h.history["mean_squared_error"])
			
			j+=1

	print("plotting the results")
	model_graph_generator(results, company["name"])
	gc.collect()

try:
	os.mkdir("./input_data")
except Exception:
	for i in Path("./input_data").iterdir():
		i.unlink()

for i in Path("./stocks").iterdir():#remove empty competitors
	if i.is_dir():
		for ii in Path(str(i)).iterdir():
			if len(ii.open("r").read()) < 30:
				ii.unlink()

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

macro_economic_factors = {"macro_factors" : {}, "oil":{}, "crypto":{}, "gold":{}, 'industry-averages':{}}
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
		for line in g.readlines():
			jline = line.split(":")
			macro_economic_factors["gold"][str(gold)]["time"].append(int(float(jline[0])))
			macro_economic_factors["gold"][str(gold)]["price"].append(jline[1])

for crude in Path("./crude_oil/").iterdir():
	macro_economic_factors['oil'][str(crude)] = {"time":[],"price":[]}
	for line in crude.open("r").readlines()[::-1]:#flipped so works?
		jline = line.split(":")

		macro_economic_factors['oil'][str(crude)]["time"].append(int(float(mstat.convert_time(jline[0]))))
		macro_economic_factors['oil'][str(crude)]["price"].append(jline[1][:jline[1].rfind(".")])

for crypto in Path("./crypto/").iterdir():
	macro_economic_factors["crypto"][str(crypto)] = {"time":[],"price":[]}
	for line in crypto.open("r").readlines():
		colon = line.split(":")
		macro_economic_factors["crypto"][str(crypto)]["time"].append(int(colon[0]))
		macro_economic_factors["crypto"][str(crypto)]["price"].append(colon[1])

for company_average in Path("./stocks/").iterdir():
	if company_average.is_dir() or not str(company_average)[str(company_average).find('/')+1:str(company_average).find('.')].isnumeric():continue
	#print(str(company_average))
	j = json.loads(company_average.open().read())
	for catj in list(j.keys()):
		if catj.find('--') != -1: del j[catj]

	macro_economic_factors["industry-averages"][str(company_average)] = j
'''
num = 0
competitors = {}
for i in Path("./stocks/").iterdir():
	if i.is_dir():
		for ii in Path(str(i)).iterdir():
			filefile = open("./"+str(ii), "r")
				
			l = json.loads(filefile.read())
			if not nn_ready(l):continue
			
			cik = (str(filefile).split("/")[-1])
			print("Finding competitor: "+str(cik[:cik.find(".")]))
			competitors[cik[:cik.find(".")]] = dict_to_arr(remove_uncommon_categories(l), True)
				
			del l
			filefile.close()
			num+=1
			gc.collect()
			#if num == 6:break


print("Loaded competitors")
'''
#so this var will be needed for network gen
gc.enable()
print("Read macro factors")
for I in Path("./stocks").iterdir():
	if I.is_dir():
		for II in Path(I).iterdir():
			with II.open("r") as f:
				comp = json.loads(f.read())
				if(nn_ready(comp)):#disabled for now
					main_wrapper(macro_economic_factors, {},comp)
					gc.collect()	

#structure: inp-sigmoid-linear is the best thus far[test layer mutation, adding H layers]
#-record on this structure: 7 mse
