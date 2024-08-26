import requests
import time
import datetime
import json

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import market_stats as mstat
import yfinance as yf
from threading import Thread

def determine_lowest(bed):
	index = len(bed)-1
	lowest = float(bed[index][0])

	for i in bed:
		if i == [""]:
			continue

		if float(i[0]) < lowest:
			index = bed.index(i)


	return index

#commodities prices and index funds
def gold_valuation():#using the nasdaq api
	starting_url = "http://data.nasdaq.com/api/v3/datasets/"
	
	try:
		os.mkdir("./gold")
	except FileExistsError:
		pass
	
	data = []
	list_of_price_values = ["CHRIS/CME_GC1", "BUNDESBANK/BBK01_WT5511", "LBMA/GOLD", "WGC/GOLD_DAILY_USD"]

	for i in list_of_price_values:
		with open("./gold/gold_"+ i.replace("/", "") + ".txt", "w+") as f: 
			try:
				info = mstat.file_request(starting_url+i, html=True)
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
		
def btc_valuation():#binance api

	try:
		os.mkdir("./crypto")
	except FileExistsError:
		pass

	with open("./crypto/btc.txt", "w+") as f:
		end = mstat.file_request("https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1", html=True).json()[0][0]
		info = []
		while True:
			data = mstat.file_request("https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&endTime="+str(end), html=True).json()
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
		
def eth_valuation():

	try:
		os.mkdir("./crypto")
	except FileExistsError:
		pass

	with open("./crypto/eth.txt", "r+") as f:
		end = mstat.file_request("https://api.binance.us/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=1", html=True).json()[0][0]
		info = []
		while True:
			data = mstat.file_request("https://api.binance.us/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=1000&endTime="+str(end), html=True).json()
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

def crude_oil():
	starting_url = "http://data.nasdaq.com/api/v3/datasets/"
	data_sources = ['CHRIS/CME_CL1', 'CHRIS/ICE_B1']

	try:
		os.mkdir("./crude_oil")
	except FileExistsError:
		pass

	for i in data_sources:
		
		data = mstat.file_request(starting_url+i, html=True).json()
		with open("./crude_oil/"+i.split("/")[1]+".txt", "r+") as f:
			for j in data["dataset"]["data"]:
				f.write(j[0]+":"+str(j[1])+ str(j[7]) +"\n")
			f.close()

def index_funds():
	inde = ["^IXIC", "^DJI", "^GSPC"]
	
	try:
		os.mkdir("./index_funds")
	except FileExistsError:
		pass

	for ind in inde:
		with open("./index_funds/"+ind.replace("^", "")+".json", "w+") as f:
			f.write(yf.Ticker(ind).history("max").to_json())
			f.close()

###personal analysis
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
	print("gathering control data")
	threads = []

	threads.append(Thread(target=gold_valuation).run())
	threads.append(Thread(target=btc_valuation).run())
	threads.append(Thread(target=eth_valuation).run())
	threads.append(Thread(target=crude_oil).run())
	threads.append(Thread(target=index_funds).run())

	for t in threads:
		try:
			t.join()
		except AttributeError:
			pass

###country financial derivatives
def treasury_interest_rate():
	url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&filter=record_date:gte:1900-01-01,security_desc:in:Federal Financing Bank&page[size]=500"#hardcoded 500 total dps
	request = (mstat.file_request(url, html=True)).json()
	del request["meta"]
	return request["data"]

def yield_curve():
	return yf.Ticker("^TYX").history("max")

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
	
	yield_data = json.loads(yield_curve().to_json())
	print("gathering treasury interest rate data")
	treasury_data = treasury_interest_rate()
	for i in treasury_data:
		try:
			data[int(float(mstat.convert_time(i["record_date"])))]["fed_interest_rate"] = float(i["avg_interest_rate_amt"])
		except KeyError:
			data[int(float(mstat.convert_time(i["record_date"])))] = {}
			data[int(float(mstat.convert_time(i["record_date"])))]["fed_interest_rate"] = float(i["avg_interest_rate_amt"])

	for y in yield_data.keys():
		for dat in (yield_data[y]).keys():
			try:
				data[int((dat.replace("00000", "00")))]["y_"+y] = float(yield_data[y][dat])
			except KeyError:
				data[int((dat.replace("00000", "00")))] = {}
				data[int((dat.replace("00000", "00")))]["y_"+y] = float(yield_data[y][dat])


	print("gathering labor stats")
	labor = labor_statistics_clump()

	for l in list(labor.keys())[::-1]:
		bell = l
		months = ['January','February','March','April','May','June','July','August','September','October','November','December']
		for m in months:
			ind = str(months.index(m)+1)
			if len(ind) == 1:
				ind = "0"+ind

			if bell.find(m) != -1:
				bell = bell.replace(m, ind)
				break

		bell = int(float(mstat.convert_time(bell)))

		if bell in data.keys():
			for k in labor[l]:
				data[bell][k] = float(labor[l][k])
		else:
			data[bell] = labor[l]

	macro.write(json.dumps(data, indent=4))
	macro.close()
