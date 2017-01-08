# FSA

#### The primary purpose of this project is to facilitate the transfer of SEC EDGAR Filings' Financial Data into custom financial statement analysis models. 

# Financial Statements
At present, I have extracted the Income Statement, Balance Sheet and Statement of Cash Flows from the 10-K filings of 68 S&P 500 companies. The statements are stored in .pkl format in order to provide for streamlined conversion into pandas objects. 

While a centralized database of pandas friendly financial statements is nice; it doesn't represent any signifcant progress. 
Accordingly, I have begun the implementation of statement standardization in order to facilitate batch comparison and multi-method valuation of equities simultaneously. 

# Fundamental Analysis of Equities
Currently, the extraction of key features from each statement has been implemented and combined in order to provide a summary
glance at important equity characteristics. For example, the high level API (callable from program run.py) will yield this
for the equity NVDA:

                    FCFE      FCFF  Cost_Debt  Cost_Equity      WACC  Weight_Debt  Weight_Equity
          2008   930.837   969.592   0.000000     5.188809  3.978022     0.235391       0.764609
          2009   154.982   114.729   0.045071     5.188809  3.978022     0.235391       0.764609
          2010  -178.408  -206.046   0.495535     5.188809  4.354444     0.177779       0.822221
          2011  -147.681  -141.953   0.282578     5.188809  3.990962     0.244148       0.755852
          2012   -44.572    25.726   0.251364     5.188809  4.174294     0.205474       0.794526
          2013   -34.864    54.133   0.226835     5.188809  4.182526     0.202799       0.797201
          2014  -201.042  -134.362   0.361625     5.188809  3.467356     0.356616       0.643384
          2015   712.660   887.195   1.529704     5.188809  3.869820     0.360468       0.639532
          2016  1926.267  2106.267   1.471730     5.188809  3.819995     0.368250       0.631750


# Valuation Models
In development. Planning on implementing DCF equity and DCF enterprise valuation methods. Need a concrete methodology for
forecasting cash flows first. 


# Macroeconomic Data

I have located my Macroeconomics textbook as well as an awesome St. Louis Fed API and am working to provide cross sectional
Analysis of the larger scale economy. This will include not only economic indicators, but also panel data structures composed
of standardized, critical components from equity financial statements, such as Net Income, Operating Expenses, Revenues, 
Debt Funding, Equity funding, and capital expenditues. Viewing the aggregate allocation of capital by publicly traded firms will
be a good compliment to the performance of individual equities as well as to the trends observed in the macro economic scope. 
