import json
import requests
from bs4 import BeautifulSoup

import math
import os

import time as t
import datetime

import personal_lib as personal
import pandas as pd

def convert_time(date):
	tim = 0
	date = date.replace("-", "")
	date = date+"000000"
	tim = str((datetime.datetime.strptime(date, "%Y%m%d%H%M%S") - datetime.datetime.utcfromtimestamp(0)).total_seconds())

	return tim

def file_request(url, to=5, html=False):
	file_str = ''
	headers = personal.random_user_agent("SEC")

	try:
		if html == False:
			file_str = requests.get(url, headers=headers, timeout=to).text
		else:
			file_str = requests.get(url, headers=headers, timeout=to)
	except requests.ConnectionError:
		t.sleep(1)
		file_request(url)
	except RecursionError:
		t.sleep(100)
		print("Error getting filling max recursion")
		file_request(url)
	except Exception:#supported to catch timeout errors idk why a specific except wont work
		t.sleep(1)
		file_request(url, to=30)

	return file_str

def search_table(lines):#consider looking for scale statements (in mill for example)
	lines = BeautifulSoup(lines.text, features="lxml")
		
	for i in lines.find_all("table"):
		try:
			i = pd.read_html(str(i))
		except ValueError as e:
			#print(e)#No tables found matching pattern '.+'
			continue
		
		outp = {}#for if the entire table is empty(funky html people)
		for row in i:#net income, and gross income/profit/margin, shareholders’
			desired_data = ["net income", "gross margin", "total shareholders’ equity"]
			row = row.dropna().to_dict()
			found_dp = {}
			outp = {}
			try:
				for key, value in row[list(row.keys())[0]].items():
					for dp in desired_data:
						if str(value).lower().find(dp) != -1:
							found_dp[key] = value.lower()

				for column in found_dp.keys():
					for i in row.keys():
						rows = row[i]
						if rows[column] != "$" and str(rows[column]).lower() != found_dp[column]:
							try:
								if column not in outp and column in desired_data:
									outp[column] = str(rows[column])
							except KeyError as e:#keeping these errors for testing whole dataset
								print(e)
			except KeyError:
				print(str(row))


	return outp

def sic_comparison(company):
	#company should be dict
	target = company["sic"]
	competitors = []
	sec_db = open("processed.json", "r")

	while True:
		line = sec_db.readline()
		if line == "": break
		if line.replace("\n", "") == "": continue

		line = json.loads(line)
		if line["sic"] == target and len(line["exchanges"]) != 0:
			competitors.append(line)

	return competitors

def sec_filling_information(company, target):#add code to examine competitors too
	company.update({"statistical data":[]})
	for i in range(len(company["filings"]["recent"]["accessionNumber"])):
		if company["filings"]["recent"]["form"][i] == target:
			filing_url = "https://www.sec.gov/Archives/edgar/data/"+company["cik"]+"/"
			fil = company["filings"]["recent"]["accessionNumber"][i].replace("-", "")
			filing_url += fil + "/" + company["filings"]["recent"]["accessionNumber"][i] + ".txt"
			request = file_request(filing_url, html=True)
			extra_stats = search_table(request)
			extra_stats["filingDate"] = company["filings"]["recent"]["filingDate"][i]
			company['statistical data'].append(extra_stats)

	return company

def treasury_interest_rate():#returns entire db
	url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&filter=record_date:gte:1900-01-01,security_desc:in:Federal Financing Bank&page[size]=500"#hardcoded 500 total dps
	request = json.loads(file_request(url))
	del request["meta"]
	f = open("fed_interest_rate.json", "w+")
	for i in request["data"]:
		f.write(json.dumps(i)+"\n")
	#print(request)


def volatility(prices):
	days = len(prices)
	s_period = math.sqrt(days)

	total = 0
	for i in prices:
		total+=i

	average=total/days
	std = 0
	for i in prices:
		std+=((i-average)**2) 

	std = std/days

	return s_period*std

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

def trends_data(company_str, execution_type=""):
	#https://trends.google.com/trends/explore?q=bi&date=now%201-d&geo=US&hl=en
	if execution_type == "update":
		url = "https://trends.google.com/trends/explore?q=" + company_str + "&date=now%201-d&geo=US&hl=en"
	else:
		url = "https://trends.google.com/trends/explore?q=" + company_str + "&date=now%all-d&geo=US&hl=en"

	interest_over_time = file_request(url)
	return interest_over_time
