# stonks

#Theory

Using NN to consider larger amounts of data for stock price prediction: below Datapoints will be converted to change values((new-prev)/prev)
- Target company: value(open, close, high, low, volume, AMA, volatility, and stock split)
- every other public company: value(like above)
- industry averages(industries are determined by SIC)
    - determined using every company in a defined SIC that is active averaged together
- index funds: value(same), used as an industrial factor too
- macro economic factors: yield curve, CPI, PPI, unemployment rate, and treasury interest rate
- control data("stable investments"): crypto, gold, oil, and index funds

#Description
- project aquires data from many sources:
    - SEC, determining industry, and quarterly reports (10q/k)
    - interbrand(when doing brand analysis), for brand valuation
    - Nasdaq api, for daily stock and commodity valuation(oil and gold)
    - yahoo finance, index fund value, alt to nasdaq for daily stock data, and treasury yield curve data
    - binance.us api, crypto daily values
    - US treasury api, for national interest rate
    - board of labor statistics, for CPI, PPI, and Unemployment rate

- data compiled to machine legible information, stored in json folder tree
- read from tree and use to train a model to accurately predict price
- display results in graphs to determine accuracy


#Improvements
- control_data.py:
    - all commodities data
      - profile/classify into type

- market_stats.py:
    - nyse api setup, would have to scrape website
    - google trends data, alternatives??
    - sec data causes 1 errors [verify]

- evaluation.py:
    - data should be presplit into test, validation, and eval
    - [fix] crashed due to memory again
    - [test]convert from next days to change each day
    - [todo]remove non full rows? vs columns
    - [do last]reintroduce statistical data
 	    - functions aren't fully reliable 
    - reintroduce competitors
    - industry averages arent added for some reason
    - classify similiar companies/companies associated with one another, nearest neighbor??
    - classify economy strength??
    - add index funds
    - add greater genetic algo batch size for hyperparmeter tuning(should use validation data instead??)
    - split data into valid, test, and training

- general:
    - make ai purchasing model DL NN
    - carbon majors, easy filter for company ethics
    - sentiment analysis
