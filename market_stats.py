#10Q for net neutral, and profit(tbd)
#bvps found in 10Q (total stockholders' equity - prefered equity)/common stock outstanding(tbd)

import json
import requests

import personal_lib as personal

def file_request(url, to=5):
	file_str = ''
	headers = personal.random_user_agent("SEC")

	try:
		file_str = requests.get(url, headers=headers, timeout=to).text
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

def sec_filling_information(company, target):
	desired_data = ["net income", "gross profit", "Total stockholders’ equity"]
	iterat=0
	for i in company["filings"]["recent"]["accessionNumber"]:
		if company["filings"]["recent"]["form"][iterat] == target:
			filing_url = "https://www.sec.gov/Archives/edgar/data/"+company["cik"]+"/"
			fil = i.replace("-", "")
			filing_url += fil + "/" + i + ".txt"
			request = file_request(filing_url).split("\n")
			hits = 0
			for line in request:
				if hits == 2:break
				for dp in desired_data:
					if line.lower().find(dp) != -1:
						print(line)#test if found right dps also scale of values?
						hits+=1

		iterat+=1


def treasury_interest_rate():#returns entire db
	url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&filter=record_date:gte:1900-01-01,security_desc:in:Federal Financing Bank&page[size]=500"#hardcoded 500 total dps
	request = json.loads(file_request(url))
	del request["meta"]
	f = open("fed_interest_rate.json", "w+")
	for i in request["data"]:
		f.write(json.dumps(i)+"\n")
	#print(request)



sec_filling_information(, "10-Q")#test
