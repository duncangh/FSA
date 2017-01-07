import settings
import os
import ExtractWorking
import pandas as pd
import numpy as np
import logs
import pickle
from DataViewer import DataView
import collections
pd.set_option('mode.chained_assignment', None)

# Make 10ks
def make_10ks(symbol):
    """
    Scraped Files ----> Financials
    """

    raw_path = '/Users/duncangh/PycharmProjects/Edgar/data/raw_data/%s/xml/10-K/' % symbol
    dates = os.listdir(raw_path)

    for date in dates:
        path = '/Users/duncangh/PycharmProjects/Edgar/data/data/%s/10-K/xml/%s/' % (symbol, date)

        # Make Directories
        make_10k_paths(symbol, date)

        # Extract First
        xtract = ExtractWorking.ExtractFilingData(symbol=symbol, date=date, ftype='10-K')

        try:  # Income Statement
            inc_data = xtract.data['cal']['roles']['StatementOfIncome']['tree']
            raw_df_inc = make_parents(inc_data)
            df_inc = make_aggregate_files(raw_df_inc)
            df_inc.to_pickle(path + 'StatementOfIncome.pkl')
        except:
            try:
                inc_data = xtract.data['cal']['roles']['StatementConsolidatedStatementOfIncome']['tree']
                raw_df_inc = make_parents(inc_data)
                df_inc = make_aggregate_files(raw_df_inc)
                df_inc.to_pickle(path + 'StatementOfIncome.pkl')
            except:
                try:
                    inc_data = xtract.data['cal']['roles']['ConsolidatedCondensedStatementsOfOperations']['tree']
                    raw_df_inc = make_parents(inc_data)
                    print('A')
                    df_inc = make_aggregate_files(raw_df_inc)
                    print('B')
                    df_inc.to_pickle(path + 'StatementOfIncome.pkl')
                    print('C')
                except:
                    print("Couldn't Find Statement of Income, here is the key tree: ", xtract.data['cal']['roles'].keys())

        try:  # Cash Flows
            cf_data = xtract.data['cal']['roles']['CashFlows']['tree']
            raw_df_cf = make_parents(cf_data)
            df_cf = make_aggregate_files(raw_df_cf)
            df_cf.to_pickle(path + 'CashFlows.pkl')
        except:
            try:
                cf_data = xtract.data['cal']['roles']['StatementConsolidatedStatementOfCashFlows']['tree']
                raw_df_cf = make_parents(cf_data)
                df_cf = make_aggregate_files(raw_df_cf)
                df_cf.to_pickle(path + 'CashFlows.pkl')
            except:
                try:
                    cf_data = xtract.data['cal']['roles']['ConsolidatedCondensedStatementsOfCashflows']['tree']
                    raw_df_cf = make_parents(cf_data)
                    df_cf = make_aggregate_files(raw_df_cf)
                    df_cf.to_pickle(path + 'CashFlows.pkl')
                except:
                    print("Couldn't Find CashFlows, here is the key tree: ", xtract.data['cal']['roles'].keys())

        try:  # Balance Sheet
            bal_data = xtract.data['cal']['roles']['BalanceSheet']['tree']
            df_bs = recursive_bs(bal_data)
            df_bs.to_pickle(path + 'BalanceSheet.pkl')

        except:
            try:
                bal_data = xtract.data['cal']['roles']['ConsolidatedBalanceSheets']['tree']
                df_bs = parse_bs(bal_data)
                df_bs.to_pickle(path + 'BalanceSheet.pkl')
            except:
                try:
                    bal_data = xtract.data['cal']['roles']['StatementConsolidatedBalanceSheet']['tree']
                    df_bs = parse_bs(bal_data)
                    df_bs.to_pickle(path + 'BalanceSheet.pkl')


                except:
                    print("Couldn't Find Balance Sheet, here is the key tree: ", xtract.data['cal']['roles'].keys())

# Make 10k Directories
def make_10k_paths(symbol, date):
    """
    Called by make_10ks to make all directories for financials
    """

    if not os.path.exists("{0}/{1}/10-K/xml".format(settings.FINANCIALS_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-K/xml".format(settings.FINANCIALS_DATA_PATH, symbol))

    base = "{0}/{1}/10-K/xml".format(settings.FINANCIALS_DATA_PATH, symbol)

    if not os.path.exists("{0}/{1}/".format(base, date)):
        os.makedirs("{0}/{1}/".format(base, date))

    path = "{0}/{1}/".format(base, date)
    return path

# Current
def flatten(d, parent_key='', sep='_'):
    """
    Flatten Ordered Dict From XML Extraction Program.
    """
    items = []
    for k, v in d.items():
        if isinstance(k, tuple):
            new_key = parent_key + sep +k[0] + sep +k[1] if parent_key else k
            nk = new_key
        else:
            if k in ['pfx', 'order', 'weight', 'label', 'terseLabel']:
                continue
            new_key = parent_key + sep + k if parent_key else k
            if k in ['sub', 'val']:
                nk = parent_key
            else:
                nk = new_key
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, nk, sep=sep).items())
        else:
            items.append((nk, v))
    return dict(items)

# Current
def make_parents(cf, is_period=True):
    """
    Parameters:
    ==============================================================================
    cf: Flattened Dictionary returned from flatten()

    is_period (optional): default=True. Override and use False for Balance Sheet
    ==============================================================================
    Returns:
    ==============================================================================
    DataFrame with TimeDelta, Formatted Time and Standardized Column Names

    """
    cf2 = flatten(cf)
    df2 = pd.DataFrame.from_dict(cf2, orient='index')

    df2['Cat'] = df2.index
    df2['Count'] = df2.Cat.apply(lambda x: len(x.split('_')[:-2]))
    high = df2.Count.values.max()

    for i in range(high + 1):
        if i == 0:
            df2['Parent'] = df2.Cat.apply(lambda x: x.split('_')[i])
        else:
            df2['Child %i' % i] = df2[df2.Count > i].Cat.apply(lambda x: x.split('_')[i])

    # Last two columns should be the dates
    if is_period == True:
        df2['Start'] = pd.to_datetime(df2.Cat.apply(lambda x: x.split('_')[-2]))
        df2['End'] = pd.to_datetime(df2.Cat.apply(lambda x: x.split('_')[-1]))

    else:
        df2['End'] = pd.to_datetime(df2.Cat.apply(lambda x: x.split('_')[-1]))
        df2['Start'] = df2['End']

    # Calc time delta
    df2['TimeDelta'] = df2['End'] - df2['Start']
    df2.reset_index(drop=True, inplace=True)

    # Forward fill levels where labels are missing
    df2 = df2.fillna(method='ffill', axis=1)

    df2['Value'] = df2[0].apply(convert_vals)  # Convert value column to float and rename
    df2.drop(['Cat', 'Count', 0, 'Start'], axis=1, inplace=True)
    return df2

# Current
def convert_vals(x):
    """Helper Function for make_parents()"""
    try:
        return float(x)
    except:
        return np.NaN

# Current
def make_aggregate_files(df2):
    """
    ===================================================
    Parameter: DataFrame as returned from make parents

    Returns 1. Pivot Table (regardless of depth)
            2. Write Pivot to excel
    ===================================================
    Pivot Table Parameters:
                            columns : [End, TimeDelta]
                            index   : [Parent, Children]
                            values  : [Value]

    """

    # Combine Columns to eliminate levels
    df2['TimeDelta'] = df2['TimeDelta'].apply(lambda x: str(round(x.days / 90)) + ' Quarters')
    df2['End'] = df2['End'].apply(lambda x: x.strftime('%B-%Y'))
    df2['Period'] = df2['End'].str.cat(df2['TimeDelta'], sep=' ')
    del df2['TimeDelta'], df2['End']

    # Get rid of all columns except for the relevant labels
    df2 = df2.iloc[:, -3:]

    columns = ['Period']
    values = 'Value'

    index = list(df2.columns[df2.columns.str.contains('Child')])

    # Make pivot, write to excel
    piv = df2.pivot_table(columns=columns, index=index, values=values)
    piv.to_excel('MMM Statement.xlsx')
    return piv

# Current
def parse_bs(data):
    flat = flatten(data)
    df = pd.DataFrame.from_dict(flat, orient='index')
    df['Category'] = df.index
    df['Date'] = df.Category.apply(lambda x: x.split('_')[-1])
    df['Field'] = df.Category.apply(lambda x: x.split('_')[-2])
    df.reset_index(drop=True, inplace=True)
    df = df[['Field', 'Date', 0]]
    df = df.groupby('Date')[['Field', 0]].apply(lambda x: x.set_index('Field')).unstack(0).T.reset_index(0, drop=True).T
    return df

# For aggregate files
def all_financials(data, base):
    base = base.replace("/extracted_data/", "/data/")
    stmts = list(data['cal']['roles'].keys())
    for stmt in stmts:
        fname = base + stmt + '.pkl'
        if not stmt.startswith('Disclosure'):
            if 'Operations' in stmt or 'Income' in stmt or 'CashFlow' in stmt or 'Earnings' in stmt:
                try:
                    print('Starting Income Section')
                    df_inc = make_parents(data['cal']['roles'][stmt]['tree'])
                    df = make_aggregate_files(df_inc)
                    df.to_pickle(fname)
                except:
                    print('Failed Income Statement')
                    pass
            else:
                try:
                    df = parse_bs(data['cal']['roles'][stmt]['tree'])
                    df.to_pickle(fname)
                except:
                    pass

def get_files(sym, kind='BalanceSheet'):
    # Get all file names (This gets those for MMM's 10-Qs)
    root = '/Users/duncangh/PycharmProjects/Edgar/data/data/%s/' % sym
    l = []
    criteria = kind

    for dir, sdir, files in os.walk(root):
        for file in files:
            if criteria in file:
                l.append(os.path.join(dir, file))
    return l

def inc_files(sym):
    root = '/Users/duncangh/PycharmProjects/Edgar/data/data/%s/' % sym
    l = []


    for dir, sdir, files in os.walk(root):
        for file in files:
            if 'Taxes' in file:
                continue
            if 'CashFlow' in file:
                continue
            if 'Income' in file:
                l.append(os.path.join(dir, file))
            else:
                continue
    return l














# Old
# Balance Sheet Helper
def recursive_bs(bs):
    frames = []
    df = make_df(bs)
    frames.append(df)
    for idx in df.index:
        try:
            bs2 = bs[idx]['sub']
            df2 = make_df(bs2, parent=idx)
            frames.append(df2)
            for ix in df2.index:
                try:
                    bs3 = bs2[ix]['sub']
                    df3 = make_df(bs3, parent=ix)
                    frames.append(df3)
                except:
                    pass
        except:
            pass
    final = pd.concat(frames).reset_index()
    final.to_excel('MMM Balance Sheet.xlsx')
    return final

# Old
# Make Balance Sheet DataFrame
def make_df(lines, parent=None):
    labels = {}
    for k, v in lines.items():
        labels[k] = {item_key: item_value for item_key, item_value in lines[k]['val'].items()}

    df = pd.DataFrame(labels).T
    if parent == None:
        df['Parent'] = df.index
    else:
        df['Parent'] = parent

    if len(df) == 0:
        raise ValueError

    return df














# Old Aggregation Technique
def aggregate_balance_sheets():
    files = get_files()
    main = pd.read_pickle(files[0]).drop('Statement', axis=1)

    for file in files:
        new = pd.read_pickle(file).drop('Statement', axis=1).iloc[:, [0, 2, 3]]
        if new.columns[1] not in main.columns:
            main = main.merge(new, on=['Parent', 'index'])

    main = main.set_index(['Parent', 'index']).sort_index()
    main = main / 1000000
    main.to_csv(os.path.expanduser('~/Google Drive/MMM.Balance Sheet.csv'))

def aggregate_inc_statements():
    files = inc_files()

    main = pd.read_pickle(files[0])

    # Todo: Columns Munging

    for file in files[:10]:
        try:
            new = pd.read_pickle(file)#.set_index('Parent')
            main = pd.concat([new, main], axis=1)
        except:
            pass

    main.to_csv(os.path.expanduser('~/Google Drive/MMM Income Statement.csv'))

def aggregate_cash_flows():
    files = get_files(kind='CashFlow')

    main = pd.read_pickle(files[0])#.set_index('Parent')
    for file in files:
        new = pd.read_pickle(file)#.set_index('Parent')
        main = pd.concat([new, main], axis=0)
        # main = main.merge(new)
    main.to_csv(os.path.expanduser('~/Google Drive/MMM.Cash Flows.csv'))

# aggregate_inc_statements()
# aggregate_balance_sheets()
# aggregate_cash_flows()


def aggregate_inc_statements_experimental():
    files = inc_files()

    main = pd.read_pickle(files[0])
    new = []
    new = clean_cols(main, new)

    for file in files[1:]:

        try:
            df = pd.read_pickle(file)
            assert isinstance(df.index, pd.indexes.range.RangeIndex)
            new = clean_cols_list(df, new)
        except  AssertionError:
            continue
    new_v = pd.Series(new).unique()

    main.columns = new_v[:11]

    # add all columns to main
    main = main.reindex(columns=new_v)

    frames = [main]
    for file in files:
        frames.append(make_clean(file))

    master = pd.concat(frames)
    master.to_csv(os.path.expanduser('~/Google Drive/MMM Income Statement.csv'))
    return frames


def make_clean(file):
    """
    Clean the column names of the DataFrames
    """
    df = pd.read_pickle(file)
    new = []
    for col in df.columns:
        if pd.isnull(col[1]):
            new.append(col[0])
        else:
            new.append(str(col[0]) + ' ' + str(col[1]))

    df.columns = new
    return df


def clean_cols_list(df, new):
    """
    Make list of all columns to be observed in set.

    Reindex main dataframe to include all columns
    """

    cols = df.columns

    for col in cols:
        if col not in new:

            if pd.isnull(col[1]):
                new.append(col[0])
            else:
                new.append(str(col[0]) + ' ' + str(col[1]))

        else:
            pass
    return new


def make_aggregate_files_old(df2):
    """
    ===================================================
    Parameter: DataFrame as returned from make parents

    Returns:   Make aggregate pickle files
    ===================================================
    Pivot Table Parameters:
                            columns : [End, TimeDelta]
                            index   : [Parent, Children]
                            values  : [Value]

    """
    columns = ['End', 'TimeDelta']
    values = 'Value'

    index = list(df2.columns[df2.columns.str.contains('Child')])
    index.insert(0, 'Parent')

    # Make pivot, write to excel
    piv = df2.pivot_table(columns=columns, index=index, values=values)
    piv.reset_index(inplace=True)
    return piv

def make_pivot(df2):
    """
    ===================================================
    Parameter: DataFrame as returned from make parents

    Returns 1. Pivot Table (regardless of depth)
            2. Write Pivot to excel
    ===================================================
    Pivot Table Parameters:
                            columns : [End, TimeDelta]
                            index   : [Parent, Children]
                            values  : [Value]

    """

    # Combine Columns to eliminate levels
    df2['TimeDelta'] = df2['TimeDelta'].apply(lambda x: str(round(x.days / 90)) + ' Quarters')
    df2['End'] = df2['End'].apply(lambda x: x.strftime('%B-%Y'))
    df2['Period'] = df2['End'].str.cat(df2['TimeDelta'], sep=' ')
    del df2['TimeDelta'], df2['End']

    # Get rid of all columns except for the relevant labels
    df2 = df2.iloc[:, -3:]

    columns = ['Period']
    values = 'Value'

    index = list(df2.columns[df2.columns.str.contains('Child')])

    # Make pivot, write to excel
    piv = df2.pivot_table(columns=columns, index=index, values=values)
    piv.to_excel('MMM Statement.xlsx')
    return piv

# Current Helper
def make_datetime_idx(df, col_nm='1 Quarter'):
    df.index = pd.Series(df.index).apply(lambda x: pd.to_datetime(x.split(' Quarters')[0][:-2])).sort_values().values
    df.columns = [col_nm]
    return df

# Current Helper
def make_datetime(df):
    df.columns = pd.Series(df.columns).apply(
        lambda x: pd.to_datetime(x.split(' Quarters')[0][:-2])).sort_values().values
    return df