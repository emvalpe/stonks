import requests
import time
import datetime
import json

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
'''
Maybe add usd valuation to this, seems hard rn, possibly https://github.com/rwieruch/purchasing-power-parity

Gold, London A.M. Fixing 	LBMA 	LBMA/GOLD (1968-2023)#only one to check for regular updates
Gold, World Gold Council 	WGC 	WGC/GOLD_DAILY_USD(1970-2020)
Gold, Bundesbank 	BUNDESBANK 	BUNDESBANK/BBK01_WT5511(1968-2016)
Gold, COMEX Gold Futures 	COMEX 	CHRIS/CME_GC1(1974-2021)
'''

def convert_time(date):
	tim = 0
	date = date.replace("-", "")
	date = date+"000000"
	tim = str((datetime.datetime.strptime(date, "%Y%m%d%H%M%S") - datetime.datetime.utcfromtimestamp(0)).total_seconds())

	return tim

def determine_lowest(bed):
	index = len(bed)-1
	lowest = float(bed[index][0])

	for i in bed:
		if i == [""]:
			continue

		if float(i[0]) < lowest:
			index = bed.index(i)


	return index


def gold_valuation(execution_type):#using the nasdaq api
	starting_url = "http://data.nasdaq.com/api/v3/datasets/"
	
	try:
		os.mkdir("./gold")
	except FileExistsError:
		pass
	
	if execution_type == "update":
		f = open("gold_average.txt", "a+")
		url = starting_url+"LBMA/GOLD"
		to_process = json.loads(requests.get(url).text)
		point = to_process["dataset"]["data"][0]
		f.write(convert_time(point[0])+":"+str(point[1])+"\n")
		f.close()

	else:
		values = []
		data = []
		list_of_price_values = ["CHRIS/CME_GC1", "BUNDESBANK/BBK01_WT5511", "LBMA/GOLD", "WGC/GOLD_DAILY_USD"]

		for i in list_of_price_values:
			f = open("./gold/gold_"+ i.replace("/", "") + ".txt", "w+")
			try:
				info = requests.get(starting_url+i).text
				to_process = json.loads(info)
			except Exception:
				print("failed at: "+i)
				continue

			for val in to_process["dataset"]["data"]:
				val[0] = convert_time(val[0])
				data.append(val[0]+":"+str(val[1])+"\n")
			
			data = reversed(data)
			f.writelines(data)
			data = []

			f.close()
		
		#now to calculate an average, doesn't work
		final = open("gold.txt", "w+")
		files = []
		lines = []
		lowest = 0

		for i in Path("./gold").iterdir():
			files.append(i.open())

		for i in files:
			lines.append((i.readline()).split(":"))

		while True:
			if lines == []:break

			lowest = determine_lowest(lines)
			final.write(lines[lowest][0]+":"+lines[lowest][1])
			lin = (files[lowest].readline()).split(":")
			if lin != [""]:
				lines[lowest] = lin
			else:
				del lines[lowest]

		final.close()

		og_data = open("gold.txt", "r")
		average_data = open("gold_average.txt", "w+")

		old = og_data.readline().split(":")
		count = 1
		total = float(old[1])

		while True:
			line = og_data.readline()
			if line == "":break
			line = (line).split(":")
			if line[0] != old[0]:
				if count == 0:
					count = 1
					try:
						total = float(old[1])
					except ValueError:
						total = 0

				average_data.write(old[0]+":"+str(total/count)+"\n")
				count = 0
				old = line
				total = 0
			else:
				old = line
				count+=1
				try:
					total+=float(line[1])
				except ValueError:
					pass

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

def eth_validation(execution_type):

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


def generate_graph():
	files = ["gold_average.txt", "./crypto/btc.txt", "./crypto/eth.txt"]
	cfiles = ["cgold_average.txt", "./crypto/cbtc.txt", "./crypto/ceth.txt"]
	'''
	lines = []
	
	combo = open("combo_data.txt", "w+")
	val_type = ""
	for i in files:
		lins = (i.readline()).split(":")
		if lins != [""]:
			lines.append(lins)

	while True:
		if lines == []:break
		lowest = determine_lowest(lines)
		
		if lowest == 0:
			val_type = "gold"
		elif lowest == 1:
			val_type = "btc"
		else:
			val_type = "eth"
		try:
			combo.write(val_type+":"+lines[lowest][0]+":"+lines[lowest][1])
		except Exception:
			print(str(lines)+"::::::"+str(lowest))
		lin = (files[lowest].readline()).split(":")
		if lin != [""]:
			lines[lowest] = lin
		else:
			del lines[lowest]

	combo.close()'''

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

def update():
	gold_valuation("update")
	btc_valuation("update")
	eth_valuation("update")
	generate_graph()

generate_graph()#update()