import json
import requests
from bs4 import BeautifulSoup, builder
import pandas as pd

#outta trim this
from colorama import Fore, Back, Style
import math
import os
import sys
import time as t
import datetime
import random as r
from io import StringIO#probably doesn't need to exist

from pytrends.request import TrendReq

#vital data aquisition and processing
def convert_time(date):
	return str((datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.datetime.utcfromtimestamp(0)).total_seconds())

def random_user_agent(typ="str"):#requests lib is very picky while selenium isn't 
    agents = open("agents.txt", "r")
    agent = r.choice(agents.readlines())
    agents.close()
    if typ == "dict":
        balls = dict()
        balls["User-Agent"] = str(agent).replace("\n", "")
        return balls

    elif typ == "SEC":
        balls = dict()
        balls["User-Agent"] = "Amazon_Inc_learning@gmail.com"
        return balls
    else:
        return agent

def file_request(url, to=5, html=False):
	file_str = ''
	headers = random_user_agent("SEC")

	try:
		if html == False:
			file_str = requests.get(url, headers=headers, timeout=to).text
		else:
			file_str = requests.get(url, headers=headers, timeout=to)
	except requests.ConnectionError:
		t.sleep(1)
		file_request(url, html=html)
	except RecursionError:
		t.sleep(100)
		print("Error getting filling max recursion")
		file_request(url, html=html)
	except requests.exceptions.ChunkedEncodingError:#can't resolve hostname
		t.sleep(600)
		file_request(url, html=html)
	except Exception:#supported to catch timeout errors idk why a specific except wont work
		t.sleep(1)
		file_request(url, to=30, html=html)

	return file_str

###some utilities
#convert month to num
def rep_month(string):
	months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
	string = string.replace(u'\xa0', ' ').replace(",", "").replace("/", " ").replace("\\", " ")
	spit = string.split(" ")
	outp = ""

	for sub in spit:
		mon = 0
		for i in months:
			bing = ""
			mon+=1

			loc = sub.find(i)
			los = sub.find(i[:3])
			if mon < 10:
				bing = "0"

			if sub.endswith(i):
				sub = sub.replace(i ,bing+str(mon))
				break
			elif sub.endswith(i[:3]):
				sub = sub.replace(i[:3] ,bing+str(mon))
				break

			if loc != -1:
				sub = sub.replace(i ,bing+str(mon))
				break
			elif loc == -1 and los != -1:
				sub = sub.replace(i[:3] ,bing+str(mon))
				break

		outp+=sub+" "

	return outp[:-1]
#start of alpha numeric in string, typically to remove many tabs and spaces
def start_alp(text):
	for i in range(len(text)):
		if text[i].isalnum():
			return text[i:]
#removes weird symbols, unicode?, and other
def just_alpha(text, spaces=False):
	if type(text) == type(1):return text
	new_str = ""
	for i in range(len(text)):
		if text[i].isalnum():
			new_str += text[i]
		elif spaces and text[i] == " ":
			new_str += text[i]

	return new_str
#prep for convert_time function
def date_to_num(date):
	if len(date) > 8:#year/month/day
		date = date.replace(" ", "").replace(",", "").replace("/", "").replace("\\", "").replace("-", "")
	
	new_date = date[4:]+date[:4]
	try:
		return int(new_date)

	except ValueError:
		return new_date


#fix at some point, revisit all
def no_col_table(lines):
	dict_ret = {}
	for t in lines.find_all("table"):
		table = str(t).split("\n")
		top = True
		top_lines = []
		other_lines = []
		for i in table:
			if t == "":continue
			if i.find("$") != -1:top = False
			
			if top and i.find("<") == -1:
				top_lines.append(i.split("  "))
			elif i.find("<") == -1:
				other_lines.append(i)
			else:
				continue

		col = []
		for i in top_lines:
			for s in i:
				if len(s) < 3:continue

				c = rep_month(s.replace(" ", ""))
				if s != c and c not in dict_ret and len(c) == 8:
					dict_ret[date_to_num(c)] = {}
					col.append(date_to_num(c))
		
		if len(list(dict_ret.keys())) == 0:continue

		for i in other_lines:
			pin = 0
			key = ""
			for p in i.split("  "):
				z = just_alpha(p)
				if len(z) < 3:continue

				if pin == 0 or key == "" and key.find(":") == -1:
					key=p
					pin+=1

				else:
					try:
						dict_ret[col[pin-1]][key] = z
					except Exception:
						continue
					pin+=1

	return dict_ret

def new_search_table(lines, is_html):
	datz = {}
	for table in lines:
		try:
			if is_html == True:
				to_dict = pd.read_html(StringIO(str(table).replace("$", "")))[0]
			else:
				to_dict = pd.read_xml(StringIO(str(table).replace("$", "")))['td']#1 is a style thing
		except ValueError:
			continue
		except Exception:
			try:
				to_dict = pd.read_html(StringIO(str(table).replace("$", "")))[0]
			except IndexError:
				continue
			except ValueError:
				continue
		try:
			tab = to_dict.dropna(axis=1, how='all').dropna(how="all")
			tab = tab.to_dict()
		except ValueError:
			continue

		result = {}#remove dups, neccessary
		for key,value in tab.items():
			if value not in result.values():
				result[key] = value
			
		tab = result

		header = ""
		for asdfasdf in tab.keys():
			header = asdfasdf
			break

		try:
			header = list(tab[header].values())
		except KeyError:
			#empty ones have noheaders?
			continue

		for p in tab.keys():
			if p == 0:continue

			possible_dates = ""
			for zz in tab[p]:
				zz = str(tab[p][zz])
				if not pd.isnull(zz):
					if type(zz) == float:
						zz = str(zz)

					if not zz.isnumeric():
						possible_dates += zz + "#"
			dat = ""
			for dates in possible_dates.split("#"):
				bat = rep_month(dates)
				if bat != dates and len(bat) <= 12 and bat.find("(")==-1:
					dat = bat
					break
				
			if dat == "":
				continue

			dat = date_to_num(dat)
			if dat not in datz.keys():datz[dat] = {}

			cont = 0
			for tib in (tab[p]).values():
				if str(header[cont]) == "nan":
					cont+=1
					continue
				if header[cont] not in (datz[dat]).keys() and not pd.isnull(tib) and just_alpha(str(tib)) != "":
					datz[dat][header[cont]] = just_alpha(str(tib))
				else:
					if not pd.isnull(tib) and just_alpha(str(tib)) != "":
						datz[dat][header[cont]] = just_alpha(str(tib))

				cont+=1
	

	return datz

def old_search_table(lines):
	desired = {}
	tab = []

	for t in BeautifulSoup(lines, "html.parser").find_all("table"):
		table = str(t)
		#print(table)
		dates = (table[table.find("<caption>")+len("<caption>"):table.find("<s>")]).split("\n")
		if dates == 0:continue#when not found
		good_dates = []
		#print(dates)
		for i in dates:
			if i == "":continue

			if len(i.split(",")) == 2:good_dates.append(rep_month(i))
			elif just_alpha(i) == "threemonthsended":continue
			elif rep_month(i) != i:good_dates.append(just_alpha(rep_month(i)))
			elif len(just_alpha(i))%4 == 0:good_dates.append(just_alpha(i))
			
		try:
			good_dates.remove("")
		except ValueError:#catch if not present
			pass

		if len(good_dates) == 2:
			for g in good_dates:good_dates[good_dates.index(g)] = rep_month(g)
			
			old = date_to_num(good_dates[0][4:]+good_dates[1][4:])
			new = date_to_num(good_dates[0][:4]+good_dates[1][:4])
			
			try:
				if not old.isnumeric():
					continue
			except AttributeError:
				try:
					if not new.isnumeric():
						continue
				except AttributeError:
					pass

			if old not in desired.keys():desired[old] = {}
			if new not in desired.keys():desired[new] = {}
			to_analyze = table[table.find("<c>")+8:]
			for p in to_analyze.split("\n"):
				p = p.replace("$", "").replace(",","")
				if just_alpha(p) != "":
					bits = p.split(" ")
					newp = []
					for bit in bits:
						if bit!="":newp.append(bit)
					if len(newp) >= 3 and newp[-1].isnumeric() and newp[-2].isnumeric():
						cat = ""
						for b in newp[:-2]:
							cat+=b+" "
						cat = cat[:-1]
						desired[old][cat] = newp[-1]
						desired[new][cat] = newp[-2]
		
	return desired	

def find_scaling_per_doc(lines):#exists because some companies don't list the exact number just 1000*100 for instance
	for p in lines.find_all("p"):
		tp = str(p.text).lower()
		if tp.find("(in") != -1 and len(tp[tp.find("(in"):tp.find("\n")-1]) < 50 and len(tp[tp.find("(in"):tp.find("\n")-1]) > 5:
			stri = tp[tp.find("(in")+3:tp.find("\n")-2].replace("\n", "")
			if stri.find("million") != -1:return "million"
			if stri.find("thousand") != -1:return "thousand"
			if stri.find("billion") != -1:return "billion"
		elif tp.find("(dollars in ") != -1 and len(tp[tp.find("(dollars in "):tp.find("\n")-1]) < 50 and len(tp[tp.find("(in"):tp.find("\n")-1]) > 5:
			stri = tp[tp.find("(dollars in ")+3:tp.find("\n")-2].replace("\n", "")
			if stri.find("million") != -1:return "million"
			if stri.find("thousand") != -1:return "thousand"
			if stri.find("billion") != -1:return "billion"

	return ""
	
#SEC based search and competitor analysis
def sic_comparison(company):
	#company should be sic
	competitors = []
	sec_db = open("processed.json", "r")

	while True:
		line = sec_db.readline()
		if line == "": break
		if line.replace("\n", "") == "": continue

		jline =  json.loads(line)
		if jline["sic"] == company and len(jline["exchanges"]) != 0:
			competitors.append(line)

	return competitors

def sec_filling_information(company, target):
	company["statisticalData"] = []
	company["fails"] = 0
	ite = 0
	bad_ite = 0

	total = 0
	start = t.time()
	
	try:
		for f in company["filings"]["recent"]["form"]:
			if f.upper() == target:total+=1
	except KeyError:
		return company
	#SEC 600/min

	for i in range(len(company["filings"]["recent"]["accessionNumber"])):
		if str(company["filings"]["recent"]["form"][i]).upper() == target or company["filings"]["recent"]["form"][i].upper().find(target) != -1:
			ite += 1
			filing_url = "https://www.sec.gov/Archives/edgar/data/"+company["cik"]+"/"
			fil = company["filings"]["recent"]["accessionNumber"][i].replace("-", "")
			filing_url += fil + "/" + company["filings"]["recent"]["accessionNumber"][i] + ".txt"
			
			extra_stats = {}

			doc = ""

			result = (file_request(filing_url))#.replace("\u2019", "'").lower().replace("\t", " ")
			try:
				for file in BeautifulSoup(result[result.find('</SEC-HEADER>')+len('</SEC-HEADER>'):],'html.parser'):
					sfile = str(file).lower()
					desc = sfile[sfile.find('<DESCRIPTION>'.lower()):]
					desc = desc[:desc.find("\n")]
					if just_alpha(desc).lower().find(just_alpha(target).lower()) != -1:
						doc = sfile
						break
					elif sfile.find("<text>") != -1:
						doc = sfile[sfile.find("<text>"):sfile.find("</text>")]
						break
					else:
						pass


			except builder.ParserRejectedMarkup as e:
				print(Fore.RED + str(e))
				company["fails"] +=1
					
			except AssertionError as g:
				print(Fore.RED + str(g))
				company["fails"] +=1
		
			if doc != "":
				if (doc.lower()).find("<s>") == -1 and (doc.lower()).find("<s>") == -1:
					doc = list(BeautifulSoup(doc, "html.parser").find_all("table"))
					#print(str(list(doc.find_all(recursive=False))))
					extra_stats = new_search_table(doc, True)
					extra_stats["method"] = 1
				else:
					extra_stats = old_search_table(doc)
					extra_stats["method"] = 2
			
				for ggg in list(extra_stats.keys()):
					try: 
						new_key = convert_time(ggg)
						old_val = extra_stats[ggg]
						del extra_stats[ggg]
						extra_stats[new_key] = old_val

					except Exception as e:
						pass
						'''
						print(e)
						print("recent mod above")'''

			else:
				extra_stats["method"] = 0
					
			#print(extra_stats["method"])
			extra_stats["url"] = filing_url
			extra_stats["filingDate"] = just_alpha(company["filings"]["recent"]["filingDate"][i])
			company['statisticalData'].append(extra_stats)

	for elem in range(len(company["statisticalData"])):
		for d in list(company["statisticalData"][elem].keys()):
			if d in ["method", "url", "filingDate"]:continue
			#print(d)
			copy = company["statisticalData"][elem][d]
			for key in list(company["statisticalData"][elem][d].keys()):
				if str(company["statisticalData"][elem][d][key]).isnumeric() and str(copy[key]).encode("ascii", "ignore").decode("ascii", "ignore") != "":
					company["statisticalData"][elem][d][str(key).encode('ascii', "ignore").decode('ascii', "ignore")] = int(str(copy[key]).encode("ascii", "ignore").decode("ascii", "ignore"))
					if str(key).encode('unicode_escape').decode('unicode_escape') != key:
						del company["statisticalData"][elem][d][key]
				else:
					del company["statisticalData"][elem][d][key]

	return company

###derivatives functions
def volatility(prices):
	days = len(prices)
	s_period = math.sqrt(days)

	total = len(prices)
	
	average=total/days
	std = 0
	for i in prices:
		std+=((float(i)-average)**2) 

	std = std/days

	return s_period*std

def all_volatilities(company, vol):
	vols = {}
	vols["time"] = []
	vols["price"] = []

	to_pass = []
	time_offset = 0

	for value in list(company["stock_price"].keys()):
		to_pass.append(company["stock_price"][value]["Open"])
		vols["time"].append(value)

		if len(to_pass) > vol:
			to_pass.pop()
			vols["price"].append(volatility(to_pass))
		elif len(to_pass) == vol:
			vols["price"].append(volatility(to_pass))
		else:
			vols["price"].append(1)
	
	return vols

def ama(prices):
	if(len(prices) == 0):
		return 1

	average = 0
	for p in prices:
		average+=float(p)

	return average/len(prices)

def all_amas(data, length):
	#do 10, 100, 365
	to_pass = []
	amas = {}
	amas["time"] = []
	amas["price"] = []

	for i in list(data["stock_price"].keys()):
		try:
			to_pass.append(data[i]["Open"])
		except Exception:
			pass#ignore for failed search of 0
		if len(to_pass) > length:
			to_pass.pop()
		
		amas["time"].append(i)
		amas["price"].append(ama(to_pass))
		
	return amas


###removed, not working sentiment analysis
def trends_data(company_str, execution_type=""):
	py = TrendReq(hl="en-US", tz=360, retries=2)
	payload = py.build_payload(kw_list=[company_str], cat=0, geo="US", timeframe="all", gprop="")

	return py.interest_over_time().to_json()
