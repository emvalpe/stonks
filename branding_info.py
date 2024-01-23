from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import random as r
import time as t
import json
import requests
import os

import market_stats as mstat
import pandas

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


def random_user_agent(typ="str"):
    agents = open("agents.txt", "r")
    agent = r.choice(agents.readlines())
    agents.close()
    if typ == "dict":
        balls = dict()
        balls["User-Agent"] = str(agent).replace("\n", "")
        return balls
    else:
        return agent


def top_brands():
	f = open("branding_output.txt", "w+")

	options = webdriver.FirefoxOptions().set_preference("general.useragent.override", random_user_agent())
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
	url = "https://query1.finance.yahoo.com/v7/finance/download/"+company["tickers"][0]+"?period1=0000000001&period2="+str(int(t.time()))+"&interval=1d&events=history&includeAdjustedClose=true"
	try:
		req = requests.get(url, headers=random_user_agent("dict"))
	except requests.exceptions.ConnectionError:
		t.sleep(1000)
		req = requests.get(url, headers=random_user_agent("dict"))

	company["stock_price"] = (req.text).split("\n")
	return company 

def volatilities(company, vol):
	vols = []

	to_pass = []
	for value in company["stock_price"][1:]:
		to_pass.append(value.split(",")[1])

		if len(to_pass) == vol:
			try:
				vols.append(mstat.volatility(to_pass))
			except ValueError:
				vols.append(vols[::-1])
			
			to_pass.pop(0)

	return vols

def company_info_loop():
	mstat.treasury_interest_rate()#only needs to be called once
	try:
		os.mkdir("./stocks")
	except FileExistsError:
		pass

	try:
		os.mkdir("./competitors")
	except Exception:
		pass

	total = 0
	replace_acronyms = {"Intel":"Intel Corp","Sony":"Sony Group Corp", "Jack Daniel's":"BROWN FORMAN CORP", "Coca-Cola":"Coca-Cola Consolidated, Inc.", "J.P. Morgan":"JPMorgan Chase & Co","McDonalds":"Yum Brands","GE":"General Electric CO", "IBM":"International Business Machines", "HSBC":"Hong Kong and Shanghai Banking", "KFC":"Yum Brands", "UPS":"United Parcel Service", "Pepsi":"PepsiCo", "Google":"Alphabet Inc.", "YouTube":"Alphabet Inc.", "Facebook":"Meta Platforms", "Instagram":"Meta Platforms", "Budweiser":"Anheuser-Busch Companies", "Pampers":"Procter & Gamble", "Nestle":"Nestlé S.A.", "Kellogg's":"WK Kellogg Co", "LinkedIn":"Microsoft", "Jack Daniel's":"Brown–Forman Corporation", "Tiffany":"Tiffany & Co", "Land Rover":"Jaguar Land Rover", "Louis Vuitton":"LVMH", "Goldman Sachs":"GOLDMAN SACHS GROUP INC", "Santander":"Banco Santander Mexico S.A.", "Mini":"British Motor Corporation", "Spotify":"Spotify Technology SA"}
	competitors = {}
	anti_duplicate_list = []

	for i in json.load(open("branding_output.txt", "r"))["companies"]:
		if i["Company"].replace("\u00e9", "e") == "mini":continue
		if i["Company"].replace("\u00e9", "e") not in replace_acronyms.keys():
			company = i["Company"].replace("\u00e9", "e")
		else:
			company = replace_acronyms.get(i["Company"].replace("\u00e9", "e"))

		if company in anti_duplicate_list:
			continue
		else:
			anti_duplicate_list.append(company)#avoid alphebet and meta duplicates

		print("Starting analysis of brand: " + company)
		companies = search_for_company(company)

		if len(companies) > 1:
			tickers = {"Salesforce, Inc.":"CRM","Apple Inc.":"AAPL", "HP INC":"HPQ", "GENERAL ELECTRIC CO":"GE", "FORD MOTOR CO":"F", "PROCTER & GAMBLE Co":"PG", "EBAY INC":"EBAY","MORGAN STANLEY":"MS"}
			match = False
			for comp in companies:
				if comp["name"] in tickers.keys():
					company = comp
					match = True
					break

			if match == False:
				company = companies[0]#idk default for now [fix]

		elif companies == []:
			print("Company may be foreign: " + company)
			continue
		else:
			company = companies[0]

		if type(company) == type(""):
			print(companies)
			continue

		company["name"] = str(company["name"]).replace("/", "")
		sec_company = company_pricing_info(company)

		if type(sec_company) == list:
			print("Multiple results for: " + company)

		start = t.time()
		print("Digging into " + sec_company["name"])
		sec_company = mstat.sec_filling_information(sec_company, "10-Q")
		sec_company["trendsData"] = mstat.trends_data(sec_company["name"])#needs testing too
		if float(sec_company["fails"])/float(len(sec_company["statisticalData"]))*100 >= 20.0:#dont use if less then 20% accurate
			print("FAILED[] finding statistical data for: "+str(sec_company["name"]))
			continue#skip dumping remaining info
		
		sec_company["vol100"] = volatilities(sec_company, 100)
		sec_company["vol365"] = volatilities(sec_company, 365)
		sec_company["vol10"] = volatilities(sec_company, 10)
		
		#fill empty categories with previous values and remove extra dates
		f = open("./stocks/"+(sec_company["tickers"][0]).lower()+".json", "w+")
		json.dump(sec_company, f, indent=4)
		f.close()
		

		print("Dug into " + sec_company["name"] + " took(min) " + str(round((t.time()-start)/60, 2)))
		if sec_company["sic"] not in competitors.keys():#used to process competitors AFTER this
			competitors[sec_company["sic"]] = sec_company["cik"]

	print("Analyzing competitors")#test [not passed]
	for i in competitors.keys():
		print("Analyzing sic: "+str(i))
		comp = mstat.sic_comparison(i)

		avg_comp = {}
		avg_comp["sic"] = i
		avg_comp["companies"] = []

		competitor = open("./competitors/"+i+".json", "w+")
		for c in comp:
			if len(list(avg_comp["companies"])) >= 10:#had to set to 10 instead of twenty, it wtoree 140 gigs for some reason
				break#this appears to be the issue

			jc = json.loads(c)
			if jc["cik"] == competitors[i] or jc["entityType"] != "operating" or len(list(jc["tickers"])) == 0:continue
			

			c = company_pricing_info(jc)
			c = mstat.sec_filling_information(c, "10-Q")
			if len(list(c["statisticalData"])) <= 10:
				continue

			c["trendsData"] = mstat.trends_data(c["name"])#needs testing too
			c["vol100"] = volatilities(c, 100)
			c["vol365"] = volatilities(c, 365)
			c["vol10"] = volatilities(c, 10)

			if float(c["fails"])/float(len(c["statisticalData"]))*100 >= 20.0:#dont use if less then 20% accurate, also seems to cause issues
				print("FAILED[] finding ENOUGH statistical data for: "+str(c["name"]))
				continue
			else:
				avg_comp["companies"].append(c)
				
		competitor.write(json.dumps(avg_comp, indent=4))
		competitor.close()				

company_info_loop()
