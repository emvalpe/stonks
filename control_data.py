import requests
import time
import datetime
import json

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import market_stats as mstat

def determine_lowest(bed):
	index = len(bed)-1
	lowest = float(bed[index][0])

	for i in bed:
		if i == [""]:
			continue

		if float(i[0]) < lowest:
			index = bed.index(i)


	return index

#commodities prices
def gold_valuation(execution_type):#using the nasdaq api
	starting_url = "http://data.nasdaq.com/api/v3/datasets/"
	
	try:
		os.mkdir("./gold")
	except FileExistsError:
		pass
	
	if execution_type == "update":
		print("not programmed yet")
		'''
		f = open("gold_average.txt", "a+")
		url = starting_url+"LBMA/GOLD"
		to_process = json.loads(requests.get(url).text)
		point = to_process["dataset"]["data"][0]
		f.write(mstat.convert_time(point[0])+":"+str(point[1])+"\n")
		f.close()'''

	else:
		data = []
		list_of_price_values = ["CHRIS/CME_GC1", "BUNDESBANK/BBK01_WT5511", "LBMA/GOLD", "WGC/GOLD_DAILY_USD"]

		for i in list_of_price_values:
			f = open("./gold/gold_"+ i.replace("/", "") + ".txt", "w+")
			try:
				info = mstat.file_request(starting_url+i)
				to_process = json.loads(info)
			except Exception:
				print("failed at: "+i)
				continue

			for val in to_process["dataset"]["data"]:
				data.append(mstat.convert_time(val[0])+":"+str(val[1])+"\n")
			
			data = reversed(data)
			f.writelines(data)
			data = []

			f.close()

def btc_valuation(execution_type):#binance api

	try:
		os.mkdir("./crypto")
	except FileExistsError:
		pass

	if execution_type == "update":
		data = requests.get("https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT")
		t = str(datetime.date.year) + "-" + str(datetime.date.month) + "-" + str(datetime.date.day)
		f = open("./crypto/btc.txt", "a+")
		f.write(t+":"+data.text)#2016-04-18 date format
		f.close()
	else:
		f = open("./crypto/btc.txt", "w+")
		end = json.loads(requests.get("https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1").text)[0][0]
		info = []
		while True:
			data = json.loads(requests.get("https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&endTime="+str(end)).text)
			temp = []
			if end == data[0][0]: break
			else: end = data[0][0]

			for i in range(len(data)):
				if i == 0:continue
				funny = data[i][:2]
				funny[0] = str(funny[0])[0:10]
				date = funny[0]
				funny = date+":"+funny[1]
				temp.append(funny+"\n")#writing one chunk in order the the second is ><
			info.append(temp)	

		balls = []
		for i in reversed(info):
			for j in i:
				balls.append(j)

		f.writelines(balls)
		f.close()#earliest date 2021-03-01

def eth_valuation(execution_type):

	try:
		os.mkdir("./crypto")
	except FileExistsError:
		pass

	if execution_type == "update":
		data = requests.get("https://api.binance.us/api/v3/ticker/price?symbol=ETHUSDT")
		t = str(datetime.date.year) + "-" + str(datetime.date.month) + "-" + str(datetime.date.day)
		f = open("./crypto/eth.txt", "a+")
		f.write(t+":"+data.text)#2016-04-18 date format
		f.close()
	else:
		f = open("./crypto/eth.txt", "w+")
		end = json.loads(requests.get("https://api.binance.us/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=1").text)[0][0]
		info = []
		while True:
			data = json.loads(requests.get("https://api.binance.us/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=1000&endTime="+str(end)).text)
			temp = []
			if end == data[0][0]: break
			else: end = data[0][0]

			for i in range(len(data)):
				if i == 0:continue
				funny = data[i][:2]
				funny[0] = str(funny[0])[0:10]
				date = funny[0]
				funny = date+":"+funny[1]
				temp.append(funny+"\n")#writing one chunk in order the the second is ><
			info.append(temp)	

		balls = []
		for i in reversed(info):
			for j in i:
				balls.append(j)

		f.writelines(balls)
		f.close()

def crude_oil(execution_type):
	starting_url = "http://data.nasdaq.com/api/v3/datasets/"
	data_sources = ['CHRIS/CME_CL1', 'CHRIS/ICE_B1']

	try:
		os.mkdir("./crude_oil")
	except FileExistsError:
		pass

	for i in data_sources:
		
		try:
			data = requests.get(starting_url+i).json()
		except requests.exceptions.JSONDecodeError:
			print("failed at: " + i)
			continue

		if execution_type == "update":
			wdir = open("./crude_oil/"+i.split("/")[1]+".txt", "a+")
			day = data["dataset"]["data"][0]

			wdir.write(day[0]+":"+str(day[1])+ str(day[7]) +"\n")
			wdir.close()
			del wdir

		else:
			wdir = open("./crude_oil/"+i.split("/")[1]+".txt", "w+")
			#print("Source: "+i)
			for j in data["dataset"]["data"]:
				wdir.write(j[0]+":"+str(j[1])+ str(j[7]) +"\n")
			
			wdir.close()

def generate_graph():
	files = ["gold_average.txt", "./crypto/btc.txt", "./crypto/eth.txt"]
	cfiles = ["cgold_average.txt", "./crypto/cbtc.txt", "./crypto/ceth.txt"]

	for i in files:
		f = open(i, "r")
		if i.find("/") != -1:
			new = i.split("/")
			c = open(new[0]+"/"+new[1]+"/"+"c"+new[2], "w+")
		else:
			c = open("c"+i, "w+")
		start = f.readline().split(":")

		while True:
			line = f.readline().split(":")
			if line == [""] or line[1] == '0.0\n':break
			try:
				num = round((float(line[1])/float(start[1]))*100, 5)
				c.write(line[0]+":"+str(num-100)+"\n")
			except Exception:
				print(i)
				print(start)
				print(line)
			start = line

		c.close()
		f.close()

	ite = 0
	for i in cfiles:
		x = []
		y = []
		f = open(i, "r")

		while True:
			line = f.readline()
			if line == "":break

			line = line.split(":")
			x.append(line[0])
			y.append(float(line[1]))

		nx = np.array(x)
		ny = np.array(y)
		if ite == 0:
			color = "red"
			ls = "-"#:

		elif ite == 1:
			color = "pink"
			ls = "-"

		else:
			color = "purple"
			ls = "-"

		#marker to show fluctuating dots(ms to change marker size, mec for color)
		plot = plt.subplot(len(cfiles), 1, ite+1)
		plt.axhline(y=0, color='black', linestyle='-')
		plt.ylabel("Value USD")
		
		plt.plot(nx, ny, color=color, ls=ls)
		#plt.setp(plot.axes.get_xticklabels(), visible=False)
		#plt.setp(plot.axes.get_xticklabels()[::10], visible=True)
		
		print("finished "+str(ite))
		ite+=1
		f.close()

	#plt.title("Control Groups")
	plt.xlabel("Time Since Epoch")

	#plt.grid(axis="x")
	plt.show()

def update():#for daily usage
	gold_valuation("update")
	btc_valuation("update")
	eth_valuation("update")
	generate_graph()

#generate_graph()#update()

gold_valuation("")
eth_valuation("")
btc_valuation("")
crude_oil("")

def treasury_interest_rate():#use for federalinterest
	url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&filter=record_date:gte:1900-01-01,security_desc:in:Federal Financing Bank&page[size]=500"#hardcoded 500 total dps
	request = (mstat.file_request(url, html=True)).json()
	del request["meta"]
	return request["data"]

def yield_curve_dep_treasury():#remove commented code if data gathered correctly
	url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/all/"
	add_1 = "?type=daily_treasury_yield_curve&field_tdr_date_value_month="
	add_2 = "&page&_format=csv"
	#the ints will be one variable decrementing by month
	data = []
	date = datetime.datetime.now()
	
	month = date.month
	year = date.year

	while year != 1900:
		y2 = year
		if int(month)-1 == 0:
			m2 = month-1

			if len(str(m2)) == 1:
				m2 = "0"+str(m2)

			y2-=1
		else:m2 = str(12)

		if len(str(month)) == 1:
			month = "0"+str(month)

		ite = 0
		req = mstat.file_request(url+str(year)+month+add_1+str(y2)+m2+add_2, to=5,html=True)
		#req = mstat.file_request(url+str(year)+str(month)+add_1+str(year)+str(month)+add_2)
		print(str(req))
		cats = []
		for i in req.split("\n"):
			if ite == 0:
				cats=i.split(",")
				ite+=1
				continue
			mod_i = {}
			cat = 0
			for comma in i.split(","):
				if cat == 0:
					mod_i["record_date"] = mstat.convert_time(comma.replace("/", "").replace("-",""))
				else:
					mod_i[cats[cat]] = comma
				cat+=1

			data.append(mod_i)

	return data

def labor_statistics_clump():

	base = 'https://api.bls.gov/publicAPI/v1/timeseries/data/'
	data = {}
	cat_convert = {"LNS14000000":"unemploymentRate", "CWUR0000SA0L1E":'CPIUrban', "WPSFD4":"PPICommodities"}

	date = datetime.datetime.now()
	year = date.year
	p = ""

	while p == "" or (p.text).find("No Data Available") != -1:
		args = {'seriesid':["LNS14000000", "CWUR0000SA0L1E", "WPSFD4"], 'startyear':str(year-10), 'endyear':str(year)}
		p = requests.post(base, data=json.dumps(args), headers={'Content-type': 'application/json'})
		year-=10
		pdata = json.loads(p.text)
		try:
			for series in pdata["Results"]["series"]:
				for item in series["data"]:
					tim = item['year']+"-"+item["periodName"]+"-01"
					if tim in data.keys():
						data[tim][cat_convert[series["seriesID"]]] = item["value"]
					else:
						data[tim] = {}
						data[tim][cat_convert[series["seriesID"]]] = item["value"]
		
		except Exception as e:
			print("change ip")

	return data	

def macro_economic_factors():
	#call above when done
	#make sure all lists are in the same order{l-g vs g-l}
	data = {}
	macro = open("macro_economic_factors.json", "w+")
	
	print("gathering treasury interest rate data")
	treasury_data = treasury_interest_rate()
	for i in treasury_data:
		data[int(float(mstat.convert_time(i["record_date"].replace("-",""))))] = {}
		data[int(float(mstat.convert_time(i["record_date"].replace("-",""))))]["fed_interest_rate"] = i["avg_interest_rate_amt"]

	print("gathering labor stats")
	labor = labor_statistics_clump()

	for l in list(labor.keys())[::-1]:
		bell = l
		months = ['January','February','March','April','May','June','July','August','September','October','November','December']
		for m in months:
			ind = str(months.index(m)+1)
			if len(ind) == 1:
				ind = "0"+ind

			if bell.find(m)!= -1:
				bell = bell.replace(m, ind)
				break

		bell = int(float(mstat.convert_time(bell.replace("-", ""))))

		if bell not in data.keys():
			data[bell] = {}

		data[bell] = labor[l]

	'''#very slow and doesnt work for some reason
	print("gathering yield curve data")
	yield_curves = yield_curve_dep_treasury()
	print(yield_curves)
	for yieldc in yield_curves:
		print(yieldc["record_date"])
		if yieldc["record_date"] in data.keys():
			data[yieldc["record_date"]].update(yieldc)
		else:
			data[yieldc["record_date"]] = yieldc
	'''
	macro.write(json.dumps(data, indent=4))
	macro.close()
