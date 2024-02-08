# stonks
A project designed to automate the downloading of data to determine if a stonk has "a good brand name" as well as determining if a stock is under or over valued. After this and the generation of some statistical factors, like AMA and volatility a model will be fed this data to predict price.

improvements: control_data.py
 - fix x axis issues (control graph)
 - get nasdaq and usd valuation
 - gold update code

improvements: market_stats.py
 - fix issue with weird table processing issue, fully remove unicode???
 
 - fix competitor functions and add any new stats introduced after removed
 [below are not implemented fully/not started, grouped below are all on the same api]
 - Consumer Price Index (CPI)
 - Gross Domestic Product (GDP)
 - Unemployment rate
 - Producer Price Index (PPI)
 - Purchasing Managers' Index (PMI)[maybe not this one]

 - Treasury yield curves ["https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202401"]

general todo:
 - make ai purchasing model DL NN
