from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import random as r
import time as t
import datetime

import json
import requests
import os, gc
from pathlib import Path

import market_stats as mstat
import control_data as control
import pandas

import nasdaqdatalink as ndl
import yfinance

def search_for_company(name):#returns list of possible candidates
	sec_data = open("processed.json", "r")
	possible_candidates = []

	while True:
		line = sec_data.readline()
		if line =="":break
		if line =="\n":continue
		
		line = json.loads(line)

		if line["name"].lower().replace("\u2019", "'").find(name.lower()) != -1:
			possible_candidates.append(line)
		elif name in line["formerNames"]:
			possible_candidates.append(line)
	pp = []
	for i in possible_candidates:
		if len(i["tickers"]) > 0 and len(i["exchanges"]) > 0:
			if str(i["exchanges"]).find("NYSE") != -1 or str(i["exchanges"]).find("Nasdaq") != -1:
				pp.append(i)
	
	for i in pp:
		if (i["name"].lower()).find(name.lower()) == -1:
			pp.remove(i)

	return pp

def top_brands():
	f = open("branding_output.txt", "w+")

	options = webdriver.FirefoxOptions().set_preference("general.useragent.override", mstat.random_user_agent())
	#options.headless = True #when debugging has concluded
	service = webdriver.firefox.service.Service(executable_path="geckodriver")

	browser = webdriver.Firefox(options=options, service=service)
	browser.get("https://interbrand.com/best-global-brands/")

	main = browser.find_element(By.TAG_NAME, "main")
	big_list = main.find_element(By.ID, "custom-best-brand").find_elements(By.TAG_NAME, "article")

	if len(big_list) == 100:
		output = {"companies":[]}
		iterat = 1
		for i in big_list:
			if iterat%5 == 0:
				ActionChains(browser).scroll_by_amount(0, 140).perform()
				t.sleep(1)

			data = {"Company":"","Ranking":""}
			h = i.find_element(By.TAG_NAME, "h2")
			sub_iter = 0
			for element in h.find_elements(By.TAG_NAME, "span"):
				if sub_iter == 0:
					data["Ranking"] = element.text
					sub_iter+=1
				else:
					data["Company"] = (element.text).replace("\u2019", "'")
			
			sub_iter = 0
			output["companies"].append(data)
			iterat+=1

		json.dump(output, f, indent=1)

	else:
		print("Something went wrong")

	browser.quit()
	f.close()

def company_pricing_info(company):
	try:
		company["stock_price"] = ndl.get("WIKI/"+company["tickers"][0].upper()).to_dict()
	except ndl.errors.data_link_error.NotFoundError:#not on the nasdaq
		company["stock_price"] = yfinance.Ticker(company["tickers"][0].upper()).history("max")
		return company
	except ndl.errors.data_link_error.InternalServerError:
		t.sleep(10)
		return company_pricing_info(company)
	except IndexError:
		return {}

	times = list(company["stock_price"]["Open"].keys())
	data = {}
	previous_data = {}
	for t in times:
		data[int(t.timestamp())] = {}
		for k in company["stock_price"].keys():
			try:
				data[int(t.timestamp())][k] = float(company["stock_price"][k][t]/previous_data[k])
			except KeyError:
				data[int(t.timestamp())][k] = float(0)
			except ZeroDivisionError:
				data[int(t.timestamp())][k] = (company["stock_price"][k][t]/1)

			previous_data[k] = company["stock_price"][k][t]

	company["stock_price"] = data
	return company 

def volatilities(company, vol):
	vols = {}
	vols["time"] = []
	vols["price"] = []

	to_pass = []
	time_offset = 0
	tp_iter = 0
	for value in list(company["stock_price"].keys()):
		try:
			to_pass.append(company["stock_price"][time_offset]["Open"])
		except Exception:
			pass#ignore for failed search of 0

		if len(to_pass) == vol and tp_iter != 0:
			vols["time"].append(value)
			vols["price"].append(mstat.volatility(to_pass))
			
			to_pass.pop()

		time_offset = value
		tp_iter += 1

	return vols

def arr_to_percent(arr):
	t = 1
	new_arr = []
	ite = 0
	for i in arr:
		if not ite:
			new_arr.append(float(t))
		elif t == 0:
			new_arr.append(float(1))
		else:
			new_arr.append(float((i/t)))
				
		t = i
		ite+=1

	return new_arr

def company_info_loop(resume=False):
	control.macro_economic_factors()#only needs to be called once, where other macro indicators will go
	ndl.ApiConfig.api_key = "D_ovDC58EdaUqmb_rzcG"
	print("got macro economic factors")
	#could easily put this in a different thread to run in the background

	if resume == False:
		try:
			os.mkdir("./stocks")
		except FileExistsError:
			for i in Path("./stocks/").iterdir():
				if i.is_dir():
					for ii in Path(i).iterdir():
						ii.unlink()
				else:
					i.open("w+").close()

	total = 0

	#used for brand test, shifting away from this
	#replace_acronyms = {"Intel":"Intel Corp","Sony":"Sony Group Corp", "Jack Daniel's":"BROWN FORMAN CORP", "Coca-Cola":"Coca-Cola Consolidated, Inc.", "J.P. Morgan":"JPMorgan Chase & Co","McDonalds":"Yum Brands","GE":"General Electric CO", "IBM":"International Business Machines", "HSBC":"Hong Kong and Shanghai Banking", "KFC":"Yum Brands", "UPS":"United Parcel Service", "Pepsi":"PepsiCo", "Google":"Alphabet Inc.", "YouTube":"Alphabet Inc.", "Facebook":"Meta Platforms", "Instagram":"Meta Platforms", "Budweiser":"Anheuser-Busch Companies", "Pampers":"Procter & Gamble", "Nestle":"Nestlé S.A.", "Kellogg's":"WK Kellogg Co", "LinkedIn":"Microsoft", "Jack Daniel's":"Brown–Forman Corporation", "Tiffany":"Tiffany & Co", "Land Rover":"Jaguar Land Rover", "Louis Vuitton":"LVMH", "Goldman Sachs":"GOLDMAN SACHS GROUP INC", "Santander":"Banco Santander Mexico S.A.", "Mini":"British Motor Corporation", "Spotify":"Spotify Technology SA"}
	anti_duplicate_list = []

	bookmark = 0
	try:
		b = open("left_off_sec.txt", "r")
		bookmark = b.read()
		b.close()
	except FileNotFoundError:
		pass

	write_to = open("left_off_sec.txt", "w+")
	tt = 0
	for btest in open("processed.json", "r").readlines():

		company = json.loads(btest)

		try:
			os.mkdir("./stocks/"+company["sic"]+"/")
		except FileExistsError as e:
			pass

		company["name"] = str(company["name"]).replace("/", "")
		if resume == True and bookmark != company["name"]:
			continue
		else:
			write_to.write(company["name"])
		#print("Starting analysis of brand: " + company["name"])

		sec_company = company_pricing_info(company)
		if len(list(sec_company.keys())) == 0:
			continue

		if type(sec_company) == list:
			print("Multiple results for: " + company)

		start = t.time()
		
		#some how here too
		sec_company = mstat.sec_filling_information(sec_company, "10-Q")
		#sec_company["trendsData"] = mstat.trends_data(sec_company["name"])#needs testing too
		if sec_company["statisticalData"] == [] or float(sec_company["fails"])/float(len(sec_company["statisticalData"]))*100 >= 20.0:#dont use if less then 20% accurate
			print("FAILED[] finding statistical data for: "+str(sec_company["name"]))
			continue#skip dumping remaining info
		
		print("Digging into " + sec_company["name"])

		vol = volatilities(sec_company, 10)
		sec_company["vol10"] = {}
		sec_company["vol10"]["time"] = vol["time"]
		sec_company["vol10"]["price"] = arr_to_percent(vol["price"])
		
		vol = volatilities(sec_company, 100)
		sec_company["vol100"] = {}
		sec_company["vol100"]["time"] = vol["time"]
		sec_company["vol100"]["price"] = arr_to_percent(vol["price"])
		
		vol = volatilities(sec_company, 365)
		sec_company["vol365"] = {}
		sec_company["vol365"]["time"] = vol["time"]
		sec_company["vol365"] = arr_to_percent(vol["price"])
		
		ama = mstat.all_amas(sec_company["stock_price"], 10)
		sec_company["ama10"] = {}
		sec_company["ama10"]["price"] = arr_to_percent(ama["price"])
		sec_company["ama10"]["time"] = ama["time"]

		ama = mstat.all_amas(sec_company["stock_price"], 100)
		sec_company["ama100"] = {}
		sec_company["ama100"]["price"] = arr_to_percent(ama["price"])
		sec_company["ama100"]["time"] = ama["time"]

		ama = mstat.all_amas(sec_company["stock_price"], 365)
		sec_company["ama365"] = {}
		sec_company["ama365"]["price"] = arr_to_percent(ama["price"])
		sec_company["ama365"]["time"] = ama["time"]

		#fill empty categories with previous values and remove extra dates
		f = open("./stocks/"+ sec_company["sic"] + "/" + (sec_company["tickers"][0]).lower()+".json", "w+")
		try:
			json.dump(sec_company, f, indent=4)
		except Exception as e:
			#print(str(e))
			f.write(json.dumps(str(sec_company), indent=4))#use to find bad keys
		f.close()
		
		print("Dug into " + sec_company["name"] + " took(min) " + str(round((t.time()-start)/60, 2)))
		
		gc.collect()

	write_to.close()

company_info_loop()
#google blocks trend data requests after two companies
#yahoo finance for everything else
# - scrape or use yfinance
# - hist = msft.history(period="1mo")#try Max/max
# - lso offers a lot of good stats that can be added to the network
