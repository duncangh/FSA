import pandas_datareader.data as web
import datetime
start = datetime.datetime(2010, 1, 1)
end = pd.to_datetime('today')
end
gdp = web.DataReader("GDP", "fred", start, end)
gdp
inflation = web.DataReader(["CPIAUCSL", "CPILFESL"], "fred", start, end)
inflation