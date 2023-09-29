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
import pytrends

def search_for_company(name):#returns list of possible candidates
	sec_data = open("processed.json", "r")
	possible_candidates = []

	while True:
		line = sec_data.readline()
		if line =="":break
		if line =="\n":continue
		
		line = json.loads(line)
		if line["name"].find(name.upper()) != -1 or line["name"].find(name.lower()) != -1 or line["name"].find(name) != -1:
			possible_candidates.append(line)
		elif name.upper() in line["acquired"] or  name.lower() in line["acquired"] or  name in line["acquired"]:
			possible_candidates.append(line)
		elif name.upper() in line["formerNames"] or name.lower() in line["formerNames"] or name in line["formerNames"]:
			possible_candidates.append(line)
	pp = []
	for i in possible_candidates:
		if len(i["tickers"]) > 0 and len(i["exchanges"]) > 0 and i["exchanges"] != [""]:
			if str(i["exchanges"]).find("NYSE") != -1 or str(i["exchanges"]).find("Nasdaq") != -1:
				pp.append(i)

	if len(pp) <= 1:
		return pp

	spp = []
	for i in pp:
		if i["name"].find(name):
			spp.append(i)

	if len(spp) == 1:
		return spp
	else:
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
					data["Company"] = element.text
			
			sub_iter = 0
			output["companies"].append(data)
			iterat+=1

		json.dump(output, f, indent=1)

	else:
		print("Something went wrong")

	browser.quit()
	f.close()

def company_pricing_info(company, total):
	companies = search_for_company(company)
	total=len(companies)
	if total == 1:
		url = "https://query1.finance.yahoo.com/v7/finance/download/"+companies[0]["tickers"][0]+"?period1=0000000001&period2="+str(int(t.time()))+"&interval=1d&events=history&includeAdjustedClose=true"
		try:
			req = requests.get(url, headers=random_user_agent("dict"))
		except requests.exceptions.ConnectionError:
			t.sleep(1000)
			req = requests.get(url, headers=random_user_agent("dict"))

		return companies[0], (req.text).split("\n")
	elif total == 0:
		#print("Company may be foreign: " + company)
		return companies, total
	else:
		return companies, total

def company_info_loop():

	try:
		os.mkdir("./stocks")
	except FileExistsError:
		pass

	total = 0
	#hardcoded ik: nke, tsla, and arbnb aint workin
	replace_acronyms = {"Coca-Cola":"Coca-Cola Consolidated, Inc.","Salesforce":"Customer relationship management", "J.P. Morgan":"JPMorgan Chase & Co","McDonald’s":"McDonalds Corp","GE":"General Electric CO", "IBM":"International Business Machines", "HSBC":"Hong Kong and Shanghai Banking", "KFC":"Yum Brands", "UPS":"United Parcel Service", "Pepsi":"PepsiCo", "Google":"Alphabet Inc.", "YouTube":"Alphabet Inc.", "Facebook":"Meta Platforms", "Instagram":"Meta Platforms", "Budweiser":"Anheuser-Busch Companies", "Pampers":"Procter & Gamble", "Nestle":"Nestlé S.A.", "Kellogg's":"Kellogg Company", "LinkedIn":"Microsoft", "Jack Daniel's":"Brown–Forman Corporation", "Tiffany":"Tiffany & Co", "Land Rover":"Jaguar Land Rover", "Louis Vuitton":"LVMH", "Goldman Sachs":"GOLDMAN SACHS GROUP INC", "Santander":"Banco Santander Mexico S.A."}

	for i in json.load(open("branding_output.txt", "r"))["companies"]:
		if i["Company"] not in replace_acronyms.keys():
			company = i["Company"]
			if company.find(" ") == -1:
				company = company+" "
		else:
			company = replace_acronyms.get(i["Company"])

		sec_company, total = company_pricing_info(company, total)
		
		if type(total) == list:#improve
			sec_company["stock_price"] = total
		elif total == 0:#foreign companies
			continue
		else:
			tickers = {"Apple Inc.":"AAPL", "HP INC":"HPQ", "GENERAL ELECTRIC CO":"GE", "FORD MOTOR CO":"F", "PROCTER & GAMBLE Co":"PG", "EBAY INC":"EBAY","MORGAN STANLEY":"MS"}
			for comp in sec_company:#weird issue where companies with the / dont quite work
				if comp["name"] in tickers.keys():
					sec_company = comp
					break

		sec_company["name"] = sec_company["name"].replace("/", "")

		start = t.time()
		#where the magic will happen
		print("Digging into " + sec_company["name"])
		#sentiment_data = mstat.trends_data(sec_company["name"])
		sec_company = mstat.sec_filling_information(sec_company, "10-Q")#will return a bigger dict, need to understand how to iter through tables
		f = open("./stocks/"+sec_company["tickers"][0]+".json", "w+")
		json.dump(sec_company, f, indent=1)
		f.close()
		print("Dug into " + sec_company["name"] + " took(min) " + str((t.time()-start)/60))

company_info_loop()
