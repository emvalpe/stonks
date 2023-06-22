from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains#new to try and imitate user input

import random as r
import time as t
import json

def random_user_agent():
    agents = open("agents.txt", "r")
    agent = r.choice(agents.readlines())
    agents.close()
    return agent

f = open("branding_output.txt", "w+")

options = webdriver.FirefoxOptions().set_preference("general.useragent.override", random_user_agent())
#options.headless = True #when debugging has concluded
service = webdriver.firefox.service.Service(executable_path="geckodriver")

browser = webdriver.Firefox(options=options, service=service)
browser.get("https://interbrand.com/best-global-brands/")

main = browser.find_element(By.TAG_NAME, "main")
big_list = main.find_element(By.ID, "custom-best-brand").find_elements(By.TAG_NAME, "article")

if len(big_list) == 100:
	output = {"comapnies":[]}
	iterat = 1
	for i in big_list:
		if iterat%5 == 0:
			ActionChains(browser).scroll_by_amount(0, 140).perform()

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
		output["comapnies"].append(data)
		iterat+=1

	json.dump(output, f, indent=4)

else:
	print("Something went wrong")

browser.quit()
f.close()