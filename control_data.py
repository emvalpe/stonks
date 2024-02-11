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

#general macro indicators
def treasury_interest_rate():#returns entire db
	url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&filter=record_date:gte:1900-01-01,security_desc:in:Federal Financing Bank&page[size]=500"#hardcoded 500 total dps
	request = (mstat.file_request(url, html=True)).json()
	del request["meta"]
	f = open("fed_interest_rate.json", "w+")
	for i in request["data"]:
		f.write(json.dumps(i)+"\n")
	f.close()
	#print(request)

def treasury_yield_curves():#will need a loop since daily values
	url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/daily-treasury-rates?fields=record_date,security_desc,avg_interest_rate_amt&filter=record_date:gte:1900-01-01,security_desc:in:Federal Financing Bank&page[size]=500"

def inflation_rate():#https://www.bls.gov/help/hlpforma.htm
	url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
	request = (requests.post(url, data=(json.dumps({"seriesid":["I bookmarked the spot for this"],"startyear":"2011", "endyear":"2014"})), headers=mstat.random_user_agent())).json()

	f = open("fed_inflation_rate.json", "w+")
	for i in request["data"]:
		f.write(json.dumps(i)+"\n")
	#print(request)


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
		
		data = json.loads(requests.get(starting_url+i).text)
		if execution_type == "update":
			wdir = open("./crude_oil/"+i.split("/")[1]+".txt", "a+")
			day = data["dataset"]["data"][0]

			wdir.write(day[0]+":"+str(day[1])+ str(day[7]) +"\n")
			wdir.close()
			del wdir

		else:
			wdir = open("./crude_oil/"+i.split("/")[1]+".txt", "w+")
			print("Source: "+i)
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

#gold_valuation("")
#eth_valuation("")
#btc_valuation("")
