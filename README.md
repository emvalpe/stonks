# stonks
A project designed to automate the downloading of data to determine if a stonk has "a good brand name" as well as determining if a stock is under or over valued. After this and the generation of some statistical factors, like AMA and volatility a model will be fed this data to predict price.

improvements: control_data.py
 - get nasdaq valuation, 'https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json?'

improvements: market_stats.py
 -remove unicode from key names[check]
 - check the input leading to doc=""[todo]

general todo:
 - make ai purchasing model DL NN
 - change the acc graphs to show the fluctuating accuracy after further training
