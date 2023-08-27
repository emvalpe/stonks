from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import random as r
import time as t
import json
import requests
import os

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
	test = open("errors.txt", "a+")
	companies = search_for_company(company)
	if len(companies) == 1:
		f = open("./stocks/"+companies[0]["tickers"][0]+".csv", "w+")
		url = "https://query1.finance.yahoo.com/v7/finance/download/"+companies[0]["tickers"][0]+"?period1=0000000001&period2="+str(int(t.time()))+"&interval=1d&events=history&includeAdjustedClose=true"
		req = requests.get(url, headers=random_user_agent("dict"))
		f.writelines(req.text)
		f.close()
		return total
	elif len(companies) == 0:
		print("Company may be foreign: " + company)
		print(total+1)
		return total+1
	else:
		test.write("Len of list: "+str(len(companies))+" For: "+company)
		test.write(str(companies)+"\n")
		return total

def company_info_loop():
	best = open("errors.txt", "w+")
	best.write(" ")
	best.close()

	try:
		os.mkdir("./stocks")
	except FileExistsError:
		pass

	total = 0
	replace_acronyms = {"GE":"General Electric", "BMW":"Bayerische Motoren Werke", "IBM":"International Business Machines", "H&M":"Hennes & Mauritz Group", "HP":" Hewlett-Packard", "HSBC":"Hong Kong and Shanghai Banking", "KFC":"Kentucky Fried Chicken", "UPS":"United States Postal Service"}

	for i in json.load(open("branding_output.txt", "r"))["companies"]:
		if i["Company"] not in replace_acronyms.keys():
			company = i["Company"]
			if company.find(" ") == -1:
				company = company+" "
		else:
			company = replace_acronyms.get(i["Company"])

		total = company_pricing_info(company, total)
