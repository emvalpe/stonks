# stonks
A project designed to automate the downloading of data to determine if a stonk has "a good brand name" as well as determining if a stock is under or over valued. After this and the generation of some statistical factors, like AMA and volatility a model will be fed this data to predict price.

improvements: control_data.py
 - get nasdaq valuation, https://data.nasdaq.com/tools/api
   - do they offer index valuations??

improvements: market_stats.py
 - check the input leading to doc=""[todo]
 - convert from future change to predicted change

improvements: evaluation.py
 - more frequent data sampling??
 - fix google trends request function
 - reintroduce statisticalData
 - convert from just next day values to net change

general todo:
 - make ai purchasing model DL NN
 - carbon majors, easy filter for company ethics
 - change the acc graphs to show the fluctuating accuracy after further training
 - industry correlation?
