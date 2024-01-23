import random as r
import re

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
        balls["User-Agent"] = "Amazon Inc learning@gmail.com"
        return balls
    else:
        return agent
    
