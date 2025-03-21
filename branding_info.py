from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

#outta trim
import random as r
import time as t
import datetime
import json
import requests
import os, gc
from pathlib import Path
import pandas
from colorama import Fore, Back, Style
from threading import Thread

import market_stats as mstat
import control_data as control

import nasdaqdatalink as ndl
import yfinance

import warnings 
warnings.filterwarnings("ignore")

###retired likely to be removed soon
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

###end of above

def company_pricing_info(company):
	try:
		company["stock_price"] = ndl.get("WIKI/"+company["tickers"][0].upper()).to_dict()
	
		times = list(company["stock_price"]["Open"].keys())
		data = {}
		previous_data = {}
		#print(1)
		for tt in times:
			data[int(tt.timestamp())] = {}
			for k in company["stock_price"].keys():
				try:
					if k in previous_data.keys():
						data[int(tt.timestamp())][k] = float((company["stock_price"][k][tt]))#-previous_data[k])) makes the values a change instead of raw
					else:
						data[int(tt.timestamp())][k] = float(company["stock_price"][k][tt])
				except KeyError:
					data[int(tt.timestamp())][k] = float(0)
				
				previous_data[k] = company["stock_price"][k][tt]

		company["stock_price"] = data
		return company 
	except (ndl.errors.data_link_error.NotFoundError, ndl.errors.data_link_error.ForbiddenError, ValueError, ndl.errors.data_link_error.DataLinkError) as e:#not on the nasdaq
		#print(2)
		#gives up to 1m updates(up to a week), 730 days for 60m
		yf = yfinance.Ticker(company["tickers"][0].upper()).history("max")

		for col in yf.columns:
			try:
				yf[col] = ((yf[col]).tolist())
			except ValueError:
				#print("this one")
				pass

		prev = {}
		company["stock_price"] = {}
		for ind in yf.index:
			idn = float(mstat.convert_time(str(ind).split(" ")[0]))
			company["stock_price"][int(idn)] = {}
			for col in yf.columns:
				
				try:
					if prev[col]:
						company["stock_price"][int(idn)][col] = float((float(yf[col][ind])-float(prev[col])))
					else:
						company["stock_price"][int(idn)][col] = float(0)
				except KeyError:
					company["stock_price"][int(idn)][col] = float(0)
				
				prev[col] = yf[col][ind]

		return company

	except ndl.errors.data_link_error.InternalServerError:
		t.sleep(10)
		return company_pricing_info(company)
	except IndexError:
		return company

def arr_to_percent(arr):#dont use, implementing is backtracking
	t = 1
	new_arr = []
	ite = 0

	for i in arr:
		if not ite:
			new_arr.append(float(0))
		elif not t:
			new_arr.append(float(0))
		else:
			try:
				new_arr.append(float((i-t)/t))
			except TypeError:
				new_arr.append(float(1))
				t=0
				ite+=1
				continue
			
		t = i
		ite+=1

		return new_arr

def company_info_loop(resume=False):
	ndl.ApiConfig.api_key = ""#fill urself
	
	if resume == False:
		#could easily put this in a different thread to run in the background
		t1 = Thread(target=control.macro_economic_factors).run()#macro update
		t2 = Thread(target=control.update).run()#update control data
		
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

	#used for brand test, shifting away from this, I theorize that using a larger ecosystem of companies will help
	#replace_acronyms = {"Intel":"Intel Corp","Sony":"Sony Group Corp", "Jack Daniel's":"BROWN FORMAN CORP", "Coca-Cola":"Coca-Cola Consolidated, Inc.", "J.P. Morgan":"JPMorgan Chase & Co","McDonalds":"Yum Brands","GE":"General Electric CO", "IBM":"International Business Machines", "HSBC":"Hong Kong and Shanghai Banking", "KFC":"Yum Brands", "UPS":"United Parcel Service", "Pepsi":"PepsiCo", "Google":"Alphabet Inc.", "YouTube":"Alphabet Inc.", "Facebook":"Meta Platforms", "Instagram":"Meta Platforms", "Budweiser":"Anheuser-Busch Companies", "Pampers":"Procter & Gamble", "Nestle":"Nestlé S.A.", "Kellogg's":"WK Kellogg Co", "LinkedIn":"Microsoft", "Jack Daniel's":"Brown–Forman Corporation", "Tiffany":"Tiffany & Co", "Land Rover":"Jaguar Land Rover", "Louis Vuitton":"LVMH", "Goldman Sachs":"GOLDMAN SACHS GROUP INC", "Santander":"Banco Santander Mexico S.A.", "Mini":"British Motor Corporation", "Spotify":"Spotify Technology SA"}

	bookmark = 0
	try:
		b = open("left_off_sec.txt", "r")
		bookmark = b.read()
		b.close()
	except FileNotFoundError:
		pass

	tt = 0
	prevtt = 0
	vist = open("processed.json", "r").readlines()

	last_update_time = t.time()

	for btest in vist:

		company = json.loads(btest)

		try:
			os.mkdir("./stocks/"+company["sic"]+"/")
		except FileExistsError as e:
			pass

		company["name"] = str(company["name"]).replace("/", "")
		if resume == True and bookmark != company["name"]:
			tt+=1
			continue

		sec_company = company_pricing_info(company)
		if "stock_price" not in sec_company.keys():
			tt+=1
			continue

		'''
		if type(sec_company) == list:
			print(Fore.RED + "Multiple results for: " + company)
		'''

		start = t.time()#for ending func
		
		'''#removing for testing sake, slows exec significantly 1-8 minutes per company to 10-30 sec
		sec_company = mstat.sec_filling_information(sec_company, "10-Q")
		#sec_company["trendsData"] = mstat.trends_data(sec_company["name"])#needs testing too
		if sec_company["statisticalData"] == [] or (sec_company["fails"])/len(sec_company["statisticalData"]) >= .8:#dont use if less then 80% success
			print(Fore.RED + "FAILED[] finding statistical data for: "+str(sec_company["name"]))
			tt+=1
			continue#skip dumping remaining info
		'''

		prog = (float(tt)/float(len(vist)))*100
		if (prog > prevtt+1 and not resume) or (not prevtt and resume):
			print(Fore.GREEN + "Progress: "+str(round(prog, 2)) + "% or " + str(tt) + "/" + str(len(vist)) + " in(min): " + str(round((t.time()-last_update_time)/60, 2)))
			last_update_time = t.time()
			prevtt = prog

		vol = mstat.all_volatilities(sec_company, 10)
		vol["prices"] = (vol["price"])
		for v in vol["time"]:
			sec_company["stock_price"][v]["vol10"] = vol["price"][vol["time"].index(v)]
		
		vol = mstat.all_volatilities(sec_company, 100)
		vol["prices"] = (vol["price"])
		for v in vol["time"]:
			sec_company["stock_price"][v]["vol100"] = vol["price"][vol["time"].index(v)]
		
		vol = mstat.all_volatilities(sec_company, 365)
		vol["prices"] = (vol["price"])
		for v in vol["time"]:
			sec_company["stock_price"][v]["vol365"] = vol["price"][vol["time"].index(v)]
		
		ama = mstat.all_amas(sec_company, 10)
		ama["prices"] = (ama["price"])
		for a in ama["time"]:
			sec_company["stock_price"][a]["ama10"] = ama["price"][ama["time"].index(a)]

		ama = mstat.all_amas(sec_company, 100)
		ama["prices"] = (ama["price"])
		for a in ama["time"]:
			sec_company["stock_price"][a]["ama100"] = ama["price"][ama["time"].index(a)]

		ama = mstat.all_amas(sec_company, 365)
		ama["prices"] = (ama["price"])
		for a in ama["time"]:
			sec_company["stock_price"][a]["ama365"] = ama["price"][ama["time"].index(a)]

		#fill empty categories with previous values and remove extra dates
		f = open("./stocks/"+ sec_company["sic"] + "/" + (sec_company["tickers"][0]).lower()+".json", "w+")
		try:
			json.dump(sec_company, f, indent=4)
		except Exception as e:#dont leave
			f.write(json.dumps(str(sec_company), indent=4))#use to find bad keys
		f.close()
				
		with open("left_off_sec.txt", "w+") as write_to:
			write_to.write(company["name"])
			write_to.close()
		
		print(Fore.BLUE + "Dug into " + sec_company["name"] + " took(min) " + str(round((t.time()-start)/60, 2)) + " (sec) "+str(round((t.time()-start), 2)))
		
		bookmark = company["name"]
		if resume:resume=False
		gc.collect()
		tt+=1

	#industry averages, last thing done
	for i in Path("./stocks/").iterdir():
		if i.is_dir():
			sic = str(i)
			sic_data = {}
			for j in Path("./"+sic+"/").iterdir():
				if str(j).find("json") != -1:
					cdata = json.loads(open(str(j), "r").read())
					for stockp in cdata["stock_price"].keys():
						if stockp not in sic_data.keys():
							sic_data[stockp] = cdata["stock_price"][stockp]
							for key in list(sic_data[stockp].keys()):
								sic_data[stockp][key+"--count"] = 1
						else:
							for key in cdata["stock_price"][stockp]:
								try:
									sic_data[stockp][key] += cdata["stock_price"][stockp][key]
								except KeyError:
									sic_data[stockp][key] = cdata["stock_price"][stockp][key]
								try:
									sic_data[stockp][key+"--count"] += 1
								except KeyError:
									sic_data[stockp][key+"--count"] = 1

			for time_ind in sic_data.keys():
				for cat in list(sic_data[time_ind].keys()):
					if cat.find("--") != -1:continue
					sic_data[time_ind][cat] = sic_data[time_ind][cat]/sic_data[time_ind][cat+"--count"]#add tag to final usable??
					#del sic_data[time_ind][cat+"--count"]

			with open(sic+".json", "w+") as g:
				if len(sic_data) == 0:
					g.close()
					Path(sic+".json").unlink()
					try:
						Path(sic+"/").rmdir()
					except OSError:
						pass
				else:
					g.write(json.dumps(sic_data, indent=4))
					g.close()

	try:
		t1.join()
		t2.join()
	except Exception:
		pass

company_info_loop()
