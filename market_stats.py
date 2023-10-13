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
	try:
		lines = BeautifulSoup((lines.text).encode('ascii', errors='ignore').strip().decode('ascii'), features="lxml")
	except Exception as t:
		print(str(t)+" : "+lines)
		
	outp = {}#for if the entire table is empty(funky html people)
	for i in lines.find_all("table"):
		try:
			i = pd.read_html(str(i))
		except ValueError as e:
			continue
		except Exception as f:#looks like this will be an IndexError??
			print(str(f)+" : "+str(i))

		matched = []
		for row in i:#net income, and gross income/profit/margin, shareholders(would have a ' but curved, removed because F unicode) equity
			desired_data = ["net income", "gross margin", "total shareholders equity"]
			row = row.dropna().to_dict()
			found_dp = {}
			try:
				broken = False
				for key, value in row[list(row.keys())[0]].items():
					for dp in desired_data:
						if str(value).lower() == dp and dp not in matched:
							found_dp[key] = value.lower()
							matched.append(dp)
							if len(matched) == len(desired_data):
								broken = True
								break
					
					if broken == True:
						break


				for column in found_dp.keys():
					for k in row.keys():
						rows = row[k]
						if rows[column] != "$" and str(rows[column]).lower() != found_dp[column]:
							try:
								if column not in outp:
									outp[found_dp[column]] = str(rows[column]).replace("$ ", "")
							except KeyError as e:#keeping these errors for testing whole dataset
								print(e)
			except KeyError:
				print(str(row))
	if outp == {}:
		outp["no data"] = lines.text
		return outp
	else:
		return outp

def sic_comparison(company):
	#company should be sic
	competitors = []
	sec_db = open("processed.json", "r")

	while True:
		line = sec_db.readline()
		if line == "": break
		if line.replace("\n", "") == "": continue

		line = json.loads(line)
		if line["sic"] == company and len(line["exchanges"]) != 0:
			competitors.append(line)

	return competitors

def sec_filling_information(company, target):#add code to examine competitors too
	company.update({"statisticalData":[]})
	ite = 0
	bad_ite = 0

	for i in range(len(company["filings"]["recent"]["accessionNumber"])):
		if str(company["filings"]["recent"]["form"][i]).upper() == target or company["filings"]["recent"]["form"][i].upper().find(target) != -1:
			ite += 1
			filing_url = "https://www.sec.gov/Archives/edgar/data/"+company["cik"]+"/"
			fil = company["filings"]["recent"]["accessionNumber"][i].replace("-", "")
			filing_url += fil + "/" + company["filings"]["recent"]["accessionNumber"][i] + ".txt"
			request = file_request(filing_url, html=True)#check if bounced request or something
			while request.status_code < 300 and request.status_code >= 200:
				t.sleep(30)
				request = file_request(filing_url, html=True)

			extra_stats = search_table(request)
			if "no data" not in extra_stats.keys():
				extra_stats["data"] = filing_url
				extra_stats["filingDate"] = company["filings"]["recent"]["filingDate"][i]
				company['statisticalData'].append(extra_stats)
			else:
				bad_ite += 1
				extra_stats["no data"] = filing_url
				extra_stats["filingDate"] = company["filings"]["recent"]["filingDate"][i]
				company['statisticalData'].append(extra_stats)

	print(str(ite)+" filings searched:"+str(bad_ite)+" filings with data extracted")
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

def trends_data(company_str, execution_type=""):
	#https://trends.google.com/trends/explore?q=bi&date=now%201-d&geo=US&hl=en
	if execution_type == "update":
		url = "https://trends.google.com/trends/explore?q=" + company_str + "&date=now%201-d&geo=US&hl=en"
	else:
		url = "https://trends.google.com/trends/explore?q=" + company_str + "&date=now%all-d&geo=US&hl=en"

	interest_over_time = file_request(url)
	return interest_over_time
