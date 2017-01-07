import os
import pandas as pd
import numpy as np
import pickle
import collections
pd.set_option('mode.chained_assignment', None)
pd.set_option('display.width', 1500)

# Helper
def make_datetime(df):
    df = df[df.columns[df.columns.str.contains('4 Quarters')]]
    df.columns = pd.Series(df.columns).apply(
        lambda x: pd.to_datetime(x.split(' Quarters')[0][:-2])).sort_values().values
    return df






class Aggregate:
    def __init__(self, sym):
        self.symbol = sym
        self.path = '/Users/duncangh/PycharmProjects/FSA/data/financials_data/%s/10-K/xml/' % sym

        self.files = self._files()
        self.balance_sheet = self.make_balance_sheet()

        self.income_statement = self.make_income_statement()
        self.cash_flows = self.make_cash_flows()

        self.statements = [self.balance_sheet, self.income_statement, self.cash_flows]

    def _files(self):
        l = []
        for dir, sdir, files in os.walk(self.path):
            for file in files:
                l.append(os.path.join(dir, file))

        return pd.Series(l)

    def column_clean(self, df):
        try:
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values
        except:
            df = make_datetime(df)
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values

        df.index.name = 'Field'
        df.reset_index(inplace=True)
        return df

    def make_balance_sheet(self):
        self.files = self.files[~self.files.str.contains('Note')]
        self.files = self.files[~self.files.str.contains('Component')]

        balance_files = self.files[self.files.str.contains('Balance')].values
        df = pd.read_pickle(balance_files[0])
        df = self.column_clean(df)

        for file in balance_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field', how='outer')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]

        df = df.fillna(0)
        return df

    def make_income_statement(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        not_balance = not_balance[~not_balance.str.contains('Comprehensive')]
        not_balance = not_balance[~not_balance.str.contains('Stock')]
        income_files = not_balance[~not_balance.str.contains('Cash')]
        income_files = income_files[(~income_files.str.contains('Taxes')) & (~income_files.str.contains('Segment')) & (
        ~income_files.str.contains('Interest')) & (~income_files.str.contains('Detail')) & (
                                    ~income_files.str.contains('Deriva')) & (
                                    ~income_files.str.contains('Share'))].values
        df = pd.read_pickle(income_files[0])
        df = self.column_clean(df)

        for file in income_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field', how='outer')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]

        df = df.fillna(0)
        return df

    def make_cash_flows(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        cash_files = not_balance[not_balance.str.contains('Cash')].values
        df = pd.read_pickle(cash_files[0])
        df = self.column_clean(df)

        for file in cash_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field', how='outer')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]

        df = df.fillna(0)
        return df





































class old2Aggregate:
    def __init__(self, sym):
        self.symbol = sym
        self.path = '/Users/duncangh/PycharmProjects/FSA/data/data/%s/10-K/xml/' % sym

        self.files = self._files()
        self.balance_sheet = self.make_balance_sheet()

        self.income_statement = self.make_income_statement()
        self.cash_flows = self.make_cash_flows()

        self.statements = [self.balance_sheet, self.income_statement, self.cash_flows]

    def _files(self):
        l = []
        for dir, sdir, files in os.walk(self.path):
            for file in files:
                l.append(os.path.join(dir, file))

        return pd.Series(l)

    def column_clean(self, df):
        try:
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values
        except:
            df = make_datetime(df)
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values

        df.index.name = 'Field'
        df.reset_index(inplace=True)
        return df

    def make_balance_sheet(self):
        self.files = self.files[~self.files.str.contains('Note')]
        self.files = self.files[~self.files.str.contains('Component')]

        balance_files = self.files[self.files.str.contains('Balance')].values
        df = pd.read_pickle(balance_files[0])
        df = self.column_clean(df)

        for file in balance_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field', how='outer')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.dropna(thresh=4)
        df = df.fillna(0)
        return df

    def make_income_statement(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        not_balance = not_balance[~not_balance.str.contains('Comprehensive')]
        not_balance = not_balance[~not_balance.str.contains('Stock')]
        income_files = not_balance[~not_balance.str.contains('Cash')]
        income_files = income_files[(~income_files.str.contains('Taxes')) & (~income_files.str.contains('Segment')) & (
        ~income_files.str.contains('Interest')) & (~income_files.str.contains('Detail')) & (
                                    ~income_files.str.contains('Deriva')) & (
                                    ~income_files.str.contains('Share'))].values
        df = pd.read_pickle(income_files[0])
        df = self.column_clean(df)

        for file in income_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field', how='outer')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.dropna(thresh=4)
        df = df.fillna(0)
        return df

    def make_cash_flows(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        cash_files = not_balance[not_balance.str.contains('Cash')].values
        df = pd.read_pickle(cash_files[0])
        df = self.column_clean(df)

        for file in cash_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field', how='outer')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.dropna(thresh=4)
        df = df.fillna(0)
        return df
class OLDAggregate:
    def __init__(self, sym):
        self.symbol = sym
        self.path = '/Users/duncangh/PycharmProjects/FSA/data/data/%s/10-K/xml/' % sym

        self.files = self._files()
        self.balance_sheet = self.make_balance_sheet()

        self.income_statement = self.make_income_statement()
        self.cash_flows = self.make_cash_flows()

        self.statements = [self.balance_sheet, self.income_statement, self.cash_flows]

    def _files(self):
        l = []
        for dir, sdir, files in os.walk(self.path):
            for file in files:
                l.append(os.path.join(dir, file))

        return pd.Series(l)

    def column_clean(self, df):
        try:
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values
        except:
            df = make_datetime(df)
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values

        df.index.name = 'Field'
        df.reset_index(inplace=True)
        return df

    def make_balance_sheet(self):
        self.files = self.files[~self.files.str.contains('Note')]
        self.files = self.files[~self.files.str.contains('Component')]

        balance_files = self.files[self.files.str.contains('Balance')].values
        df = pd.read_pickle(balance_files[0])
        df = self.column_clean(df)

        for file in balance_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def make_income_statement(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        not_balance = not_balance[~not_balance.str.contains('Comprehensive')]
        not_balance = not_balance[~not_balance.str.contains('Stock')]
        income_files = not_balance[~not_balance.str.contains('Cash')]
        income_files = income_files[(~income_files.str.contains('Taxes')) & (~income_files.str.contains('Segment')) & (
        ~income_files.str.contains('Interest')) & (~income_files.str.contains('Detail')) & (
                                    ~income_files.str.contains('Deriva')) & (
                                    ~income_files.str.contains('Share'))].values
        df = pd.read_pickle(income_files[0])
        df = self.column_clean(df)

        for file in income_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def make_cash_flows(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        cash_files = not_balance[not_balance.str.contains('Cash')].values
        df = pd.read_pickle(cash_files[0])
        df = self.column_clean(df)

        for file in cash_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df
class oldv2Aggregate:
    def __init__(self, sym):
        self.symbol = sym
        self.path = '/Users/duncangh/PycharmProjects/Edgar/data/data/%s/10-K/xml/' % sym

        self.files = self._files()
        self.balance_sheet = self.make_balance_sheet()

        self.income_statement = self.make_income_statement()
        self.cash_flows = self.make_cash_flows()

        self.statements = [self.balance_sheet, self.income_statement, self.cash_flows]

    def _files(self):
        l = []
        for dir, sdir, files in os.walk(self.path):
            for file in files:
                l.append(os.path.join(dir, file))

        return pd.Series(l)

    def column_clean(self, df):
        try:
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values
        except:
            df = make_datetime(df)
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values

        df.index.name = 'Field'
        df.reset_index(inplace=True)
        return df

    def make_balance_sheet(self):
        self.files = self.files[~self.files.str.contains('Note')]
        self.files = self.files[~self.files.str.contains('Component')]

        balance_files = self.files[self.files.str.contains('Balance')].values
        df = pd.read_pickle(balance_files[0])
        df = self.column_clean(df)

        for file in balance_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def make_income_statement(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        income_files = not_balance[~not_balance.str.contains('Cash')]
        income_files = income_files[(~income_files.str.contains('Taxes')) & (~income_files.str.contains('Segment')) & (
        ~income_files.str.contains('Interest')) & (~income_files.str.contains('Detail')) & (
                                    ~income_files.str.contains('Deriva')) & (
                                    ~income_files.str.contains('Share'))].values
        df = pd.read_pickle(income_files[0])
        df = self.column_clean(df)

        for file in income_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def make_cash_flows(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        cash_files = not_balance[not_balance.str.contains('Cash')].values
        df = pd.read_pickle(cash_files[0])
        df = self.column_clean(df)

        for file in cash_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df
class oldAggregate:

    def __init__(self, sym):
        self.symbol = sym
        self.path = '/Users/duncangh/PycharmProjects/Edgar/data/data/%s/10-K/xml/' % sym

        self.files = self._files()
        self.balance_sheet = self.make_balance_sheet()

        self.income_statement = self.make_income_statement()
        self.cash_flows = self.make_cash_flows()

        self.statements = [self.balance_sheet, self.income_statement, self.cash_flows]

    def _files(self):
        l = []
        for dir, sdir, files in os.walk(self.path):
            for file in files:
                l.append(os.path.join(dir, file))

        return pd.Series(l)


    def column_clean(self, df):
        try:
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values
        except:
            df = make_datetime(df)
            df.columns = pd.DatetimeIndex(df.columns).year
            df.columns = pd.Series(df.columns).apply(lambda x: str(x)).values

        df.index.name = 'Field'
        df.reset_index(inplace=True)
        return df


    def make_balance_sheet(self):

        balance_files = self.files[self.files.str.contains('Balance')].values
        df = pd.read_pickle(balance_files[0])
        df = self.column_clean(df)

        for file in balance_files[1:]:

            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df


    def make_income_statement(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        income_files = not_balance[~not_balance.str.contains('Cash')].values
        df = pd.read_pickle(income_files[0])
        df = self.column_clean(df)

        for file in income_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def make_cash_flows(self):
        not_balance = self.files[~self.files.str.contains('Balance')]
        cash_files = not_balance[not_balance.str.contains('Cash')].values
        df = pd.read_pickle(cash_files[0])
        df = self.column_clean(df)

        for file in cash_files[1:]:
            df2 = pd.read_pickle(file)
            df2 = self.column_clean(df2)
            df = df.merge(df2, on='Field')

        df.columns = pd.Series(df.columns).apply(lambda x: str(x)[:4])
        df.set_index('Fiel', inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df



































# This works. Can be made better
def combine_10k(trio):
    frames = []

    for tr in trio:
        df = pd.read_pickle(tr)
        try:
            df.columns = pd.DatetimeIndex(df.columns).year
        except:
            df = make_datetime(df)
            df.columns = pd.DatetimeIndex(df.columns).year
        df['Statement'] = tr.split('/')[-1][:-4]
        frames.append(df)

    final = pd.concat(frames)
    final.reset_index(inplace=True)
    final.set_index(['Statement', 'index'], inplace=True)
    final.sort_index(axis=1, inplace=True)
    return final




# files = pd.Series([ '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2009-12-31/StatementOfCashFlowsIndirect.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2009-12-31/StatementOfIncome.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2010-12-31/StatementConsolidatedBalanceSheets.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2010-12-31/StatementConsolidatedStatementsOfCashFlows.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2010-12-31/StatementConsolidatedStatementsOfOperations.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2011-12-31/StatementConsolidatedBalanceSheets.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2011-12-31/StatementConsolidatedStatementsOfCashFlows.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2011-12-31/StatementConsolidatedStatementsOfOperations.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2012-12-31/ConsolidatedBalanceSheets.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2012-12-31/ConsolidatedStatementsOfCashFlows.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2012-12-31/ConsolidatedStatementsOfOperations.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2013-12-31/ConsolidatedBalanceSheets.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2013-12-31/ConsolidatedStatementsOfCashFlows.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2013-12-31/ConsolidatedStatementsOfOperations.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2014-12-31/ConsolidatedBalanceSheets.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2014-12-31/ConsolidatedStatementsOfCashFlows.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2014-12-31/ConsolidatedStatementsOfOperations.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2015-12-31/ConsolidatedBalanceSheets.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2015-12-31/ConsolidatedStatementsOfCashFlows.pkl',
#  '/Users/duncangh/PycharmProjects/Edgar/data/data/NFLX/10-K/xml/2015-12-31/ConsolidatedStatementsOfOperations.pkl'])
# bal = files[files.str.contains('Balance')]
#
# df = pd.read_pickle(file)
# df.columns = pd.DatetimeIndex(df.columns).year
# df['Statement'] = 'Balance'
# balances.append(df)

