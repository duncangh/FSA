import settings
import os
import logs
import pandas as pd
import numpy as np
import pickle
import ExtractWorking
import collections
from DataViewer import DataView
from Graham.helpers import *
from Graham.statement_structure import *
import EdgarScrapeWorking as es
from Graham.helperClass import Financial
pd.set_option('mode.chained_assignment', None)



def get_financials(symbol):

    # data/raw_data/symbol/xml/10-Q/
    # data/raw_data/symbol/xml/10-Q/
    q_path = "{0}/{1}/xml/{2}/".format(settings.RAW_DATA_PATH, symbol, '10-Q')
    k_path = "{0}/{1}/xml/{2}/".format(settings.RAW_DATA_PATH, symbol, '10-K')
    q_list = os.listdir(q_path)
    k_list = os.listdir(k_path)

    # Create directories for extraction if they do not exist
    if not os.path.exists("{0}/{1}/".format(settings.EXTRACTED_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/".format(settings.EXTRACTED_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-Q/".format(settings.EXTRACTED_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-Q/".format(settings.EXTRACTED_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-Q/xml".format(settings.EXTRACTED_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-Q/xml".format(settings.EXTRACTED_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-K/".format(settings.EXTRACTED_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-K/".format(settings.EXTRACTED_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-K/xml".format(settings.EXTRACTED_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-K/xml".format(settings.EXTRACTED_DATA_PATH, symbol))

    xml_10q_path = "{0}/{1}/10-Q/xml".format(settings.EXTRACTED_DATA_PATH, symbol)
    xml_10k_path = "{0}/{1}/10-K/xml".format(settings.EXTRACTED_DATA_PATH, symbol)

    xml_10q_path_stmt = xml_10q_path.replace('extracted_data', 'financials_data')
    xml_10k_path_stmt = xml_10k_path.replace('extracted_data', 'financials_data')

    # Create directories for Financial Data if they do not exist
    if not os.path.exists("{0}/{1}/".format(settings.FINANCIALS_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/".format(settings.FINANCIALS_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-Q/".format(settings.FINANCIALS_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-Q/".format(settings.FINANCIALS_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-Q/xml".format(settings.FINANCIALS_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-Q/xml".format(settings.FINANCIALS_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-K/".format(settings.FINANCIALS_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-K/".format(settings.FINANCIALS_DATA_PATH, symbol))

    if not os.path.exists("{0}/{1}/10-K/xml".format(settings.FINANCIALS_DATA_PATH, symbol)):
        os.makedirs("{0}/{1}/10-K/xml".format(settings.FINANCIALS_DATA_PATH, symbol))

    # 10-Q Extract

    for ql in q_list:
        if not os.path.exists("{0}/{1}".format(xml_10q_path, ql)):
            os.makedirs("{0}/{1}".format(xml_10q_path, ql))

        if not os.path.exists("{0}/{1}".format(xml_10q_path_stmt, ql)):
            os.makedirs("{0}/{1}".format(xml_10q_path_stmt, ql))

        ql_path = "{0}/{1}/".format(xml_10q_path, ql)

        try:
            tmp_xe = ExtractWorking.ExtractFilingData(symbol, ql, '10-Q')
        except:
            logs.add_extract_data(symbol, ql, False)
            continue

        if settings.OUTPUT_PICKLE:
            if tmp_xe.data['error'] == False:
                pickle.dump(tmp_xe.data, open("{0}/{1}.p".format(ql_path, tmp_xe.format_str), "wb"))
                logs.add_extract_data(symbol, ql, True)
                try:
                    Financial(tmp_xe.data, ql_path)
                except:
                    print('Error Extracting Financials: {0} | {1} | {2}'.format(symbol, ql, '10-Q'))

                pass
            elif tmp_xe.data['error'] == True:
                print('Error Extracting: {0}|{1}|{2}'.format(symbol, ql, '10-Q'))
                logs.add_extract_data(symbol, ql, False)
                pass

    # 10-K Extract
    raw_10k_path = 'data/raw_data/%s/xml/10-K/' % symbol
    # raw_10k_path = '/Users/duncangh/PycharmProjects/FSA/data/raw_data/%s/xml/10-K/' % symbol
    dates_10k = os.listdir(raw_10k_path)

    for date in dates_10k:
        final_k_path = make_10k_paths(symbol, date)

        try:
            tmp_ke = ExtractWorking.ExtractFilingData(symbol, date, '10-K')
            Financial(tmp_ke.data, final_k_path)
        except:
            pass



# get_financials('AFL')
# get_financials('T')
# get_financials('EBAY')
# get_financials('ORCL')
# get_financials('NFLX')
# es.GetFilings('MSFT')
# get_financials('MSFT')

def run():
    oldsymbols = ['WDC', 'NOC', 'FLS', 'ESS', 'JNJ', 'HUM', 'AON', 'GWW', 'ZTS',
     'HPE', 'ETN', 'HAL', 'HST', 'MCK', 'CL', 'TRV', 'BA', 'XRX', 'ED',
     'ETFC', 'GPC', 'HCP', 'DLPH', 'D', 'TSCO', 'BIIB', 'CHRW', 'BHI',
     'PKI', 'KHC', 'TRIP', 'LH', 'JEC', 'PG', 'ADS', 'EXPD', 'BEN',
     'FTV', 'VMC', 'BLL', 'SCG', 'AVY', 'CXO', 'RHT', 'VRSK', 'INTU',
     'GE', 'AXP', 'CAH', 'APD']
    symbols = ['ABT', 'ABBV', 'ACN', 'ATVI', 'AYI', 'ADBE', 'AAP', 'AES',
              'AET', 'AMG', 'AFL', 'A', 'AKAM', 'ALK', 'ALB', 'AA', 'ALXN',
              'ALLE', 'AGN', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AEE',
              'AAL', 'AEP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN',
              'APH', 'APC', 'ADI', 'ANTM', 'APA', 'AIV', 'AAPL', 'AMAT', 'ADM',
              'AJG', 'AIZ', 'T', 'ADSK', 'ADP', 'AN', 'AZO', 'AVGO', 'AVB', 'BAC',
              'BCR', 'BAX', 'BBT', 'BDX', 'BBBY', 'BRK-B', 'BBY', 'BLK', 'HRB',
              'BWA', 'BXP', 'BSX', 'BMY', 'BF-B', 'CA', 'COG', 'CPB', 'COF',
              'KMX', 'CCL', 'CAT', 'CBG', 'CBS', 'CELG', 'CNC', 'CNP', 'CTL',
              'CERN', 'CF', 'SCHW', 'CHK', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'XEC',
              'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CTXS', 'CME', 'CMS', 'COH',
              'CTSH', 'CMCSA', 'CMA', 'CAG', 'COP', 'STZ', 'GLW', 'COST', 'CCI',
              'CSRA', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE',
              'DAL', 'XRAY', 'DVN', 'DO', 'DLR', 'DFS', 'DISCA', 'DISCK', 'DG',
              'DLTR', 'DOV', 'DOW', 'DPS', 'DTE', 'DD', 'DUK', 'DNB', 'EMN',
              'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMC', 'EMR', 'ENDP', 'ETR',
              'EOG', 'EQT', 'EFX', 'EQIX', 'EQR', 'EL', 'ES', 'EXC', 'EXPE',
              'ESRX', 'EXR', 'XOM', 'FFIV', 'FB', 'FAST', 'FRT', 'FDX', 'FIS',
              'FITB', 'FSLR', 'FE', 'FISV', 'FLIR', 'FLR', 'FMC', 'FTI', 'FL',
              'F', 'FBHS', 'FCX', 'FTR', 'GPS', 'GRMN', 'GD', 'GGP', 'GIS', 'GM',
              'GILD', 'GPN', 'GS', 'GT', 'HBI', 'HOG', 'HAR', 'HRS', 'HIG', 'HAS',
              'HCA', 'HP', 'HSIC', 'HES', 'HOLX', 'HD', 'HON', 'HRL', 'HPQ',
              'HBAN', 'ITW', 'ILMN', 'IR', 'INTC', 'ICE', 'IBM', 'IP', 'IPG',
              'IFF', 'ISRG', 'IVZ', 'IRM', 'JBHT', 'JCI', 'JPM', 'JNPR', 'KSU',
              'K', 'KEY', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS', 'KR', 'LB', 'LLL',
              'LRCX', 'LM', 'LEG', 'LEN', 'LUK', 'LVLT', 'LLY', 'LNC', 'LLTC',
              'LKQ', 'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M', 'MNK', 'MRO',
              'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MAT', 'MKC', 'MCD', 'MJN',
              'MDT', 'MRK', 'MET', 'KORS', 'MCHP', 'MU', 'MSFT', 'MHK', 'TAP',
              'MDLZ', 'MON', 'MNST', 'MCO', 'MS', 'MSI', 'MUR', 'MYL', 'NDAQ',
              'NOV', 'NAVI', 'NTAP', 'NFLX', 'NWL', 'NFX', 'NEM', 'NWSA', 'NWS',
              'NEE', 'NLSN', 'NKE', 'NI', 'NBL', 'JWN', 'NSC', 'NTRS', 'NRG',
              'NUE', 'NVDA', 'ORLY', 'OXY', 'OMC', 'OKE', 'OI', 'PCAR',
              'PH', 'PDCO', 'PAYX', 'PYPL', 'PNR', 'PBCT', 'PEP', 'PRGO', 'PFE',
              'PCG', 'PM', 'PSX', 'PNW', 'PXD', 'PBI', 'PNC', 'RL', 'PPG', 'PPL',
              'PX', 'PCLN', 'PFG', 'PGR', 'PLD', 'PRU', 'PEG', 'PSA', 'PHM',
              'PVH', 'QRVO', 'QCOM', 'PWR', 'DGX', 'RRC', 'RTN', 'O', 'REGN',
              'RF', 'RSG', 'RAI', 'RHI', 'ROK', 'COL', 'ROP', 'ROST', 'RCL', 'R',
              'SPGI', 'CRM', 'SLB', 'SNI', 'STX', 'SEE', 'SRE', 'SHW', 'SIG',
              'SPG', 'SWKS', 'SLG', 'SJM', 'SNA', 'SO', 'LUV', 'SWN', 'SE', 'STJ',
              'SWK', 'SPLS', 'SBUX', 'HOT', 'STT', 'SRCL', 'SYK', 'STI', 'SYMC',
              'SYF', 'SYY', 'TROW', 'TGT', 'TEL', 'TGNA', 'TDC', 'TSO', 'TXN',
              'TXT', 'BK', 'CLX', 'KO', 'HSY', 'MOS', 'DIS', 'TMO', 'TIF', 'TWX',
              'TJX', 'TMK', 'TSS', 'TDG', 'RIG', 'FOXA', 'FOX', 'TYC', 'TSN',
              'USB', 'UDR', 'ULTA', 'UA', 'UNP', 'UAL', 'UNH', 'UPS', 'URI',
              'UTX', 'UHS', 'UNM', 'URBN', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN',
              'VZ', 'VRTX', 'VIAB', 'V', 'VNO', 'WMT', 'WBA', 'WM', 'WAT', 'WFC',
              'HCN', 'WU', 'WRK', 'WY', 'WHR', 'WFM', 'WMB', 'WLTW', 'WEC', 'WYN',
              'WYNN', 'XEL', 'XLNX', 'XL', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZION',
              'SPY']

    for sym in symbols:
        es.GetFilings(sym)
        get_financials(sym)


run()



















scrape = ['ABT', 'ABBV', 'ACN', 'ATVI', 'AYI', 'ADBE', 'AAP', 'AES',
       'AET', 'AMG', 'AFL', 'A', 'AKAM', 'ALK', 'ALB', 'AA', 'ALXN',
       'ALLE', 'AGN', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AEE',
       'AAL', 'AEP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN',
       'APH', 'APC', 'ADI', 'ANTM', 'APA', 'AIV', 'AAPL', 'AMAT', 'ADM',
       'AJG', 'AIZ', 'T', 'ADSK', 'ADP', 'AN', 'AZO', 'AVGO', 'AVB', 'BAC',
       'BCR', 'BAX', 'BBT', 'BDX', 'BBBY', 'BRK-B', 'BBY', 'BLK', 'HRB',
       'BWA', 'BXP', 'BSX', 'BMY', 'BF-B', 'CA', 'COG', 'CPB', 'COF',
       'KMX', 'CCL', 'CAT', 'CBG', 'CBS', 'CELG', 'CNC', 'CNP', 'CTL',
       'CERN', 'CF', 'SCHW', 'CHK', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'XEC',
       'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CTXS', 'CME', 'CMS', 'COH',
       'CTSH', 'CMCSA', 'CMA', 'CAG', 'COP', 'STZ', 'GLW', 'COST', 'CCI',
       'CSRA', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE',
       'DAL', 'XRAY', 'DVN', 'DO', 'DLR', 'DFS', 'DISCA', 'DISCK', 'DG',
       'DLTR', 'DOV', 'DOW', 'DPS', 'DTE', 'DD', 'DUK', 'DNB', 'EMN',
       'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMC', 'EMR', 'ENDP', 'ETR',
       'EOG', 'EQT', 'EFX', 'EQIX', 'EQR', 'EL', 'ES', 'EXC', 'EXPE',
       'ESRX', 'EXR', 'XOM', 'FFIV', 'FB', 'FAST', 'FRT', 'FDX', 'FIS',
       'FITB', 'FSLR', 'FE', 'FISV', 'FLIR', 'FLR', 'FMC', 'FTI', 'FL',
       'F', 'FBHS', 'FCX', 'FTR', 'GPS', 'GRMN', 'GD', 'GGP', 'GIS', 'GM',
       'GILD', 'GPN', 'GS', 'GT', 'HBI', 'HOG', 'HAR', 'HRS', 'HIG', 'HAS',
       'HCA', 'HP', 'HSIC', 'HES', 'HOLX', 'HD', 'HON', 'HRL', 'HPQ',
       'HBAN', 'ITW', 'ILMN', 'IR', 'INTC', 'ICE', 'IBM', 'IP', 'IPG',
       'IFF', 'ISRG', 'IVZ', 'IRM', 'JBHT', 'JCI', 'JPM', 'JNPR', 'KSU',
       'K', 'KEY', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS', 'KR', 'LB', 'LLL',
       'LRCX', 'LM', 'LEG', 'LEN', 'LUK', 'LVLT', 'LLY', 'LNC', 'LLTC',
       'LKQ', 'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M', 'MNK', 'MRO',
       'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MAT', 'MKC', 'MCD', 'MJN',
       'MDT', 'MRK', 'MET', 'KORS', 'MCHP', 'MU', 'MSFT', 'MHK', 'TAP',
       'MDLZ', 'MON', 'MNST', 'MCO', 'MS', 'MSI', 'MUR', 'MYL', 'NDAQ',
       'NOV', 'NAVI', 'NTAP', 'NFLX', 'NWL', 'NFX', 'NEM', 'NWSA', 'NWS',
       'NEE', 'NLSN', 'NKE', 'NI', 'NBL', 'JWN', 'NSC', 'NTRS', 'NRG',
       'NUE', 'NVDA', 'ORLY', 'OXY', 'OMC', 'OKE', 'OI', 'PCAR',
       'PH', 'PDCO', 'PAYX', 'PYPL', 'PNR', 'PBCT', 'PEP', 'PRGO', 'PFE',
       'PCG', 'PM', 'PSX', 'PNW', 'PXD', 'PBI', 'PNC', 'RL', 'PPG', 'PPL',
       'PX', 'PCLN', 'PFG', 'PGR', 'PLD', 'PRU', 'PEG', 'PSA', 'PHM',
       'PVH', 'QRVO', 'QCOM', 'PWR', 'DGX', 'RRC', 'RTN', 'O', 'REGN',
       'RF', 'RSG', 'RAI', 'RHI', 'ROK', 'COL', 'ROP', 'ROST', 'RCL', 'R',
       'SPGI', 'CRM', 'SLB', 'SNI', 'STX', 'SEE', 'SRE', 'SHW', 'SIG',
       'SPG', 'SWKS', 'SLG', 'SJM', 'SNA', 'SO', 'LUV', 'SWN', 'SE', 'STJ',
       'SWK', 'SPLS', 'SBUX', 'HOT', 'STT', 'SRCL', 'SYK', 'STI', 'SYMC',
       'SYF', 'SYY', 'TROW', 'TGT', 'TEL', 'TGNA', 'TDC', 'TSO', 'TXN',
       'TXT', 'BK', 'CLX', 'KO', 'HSY', 'MOS', 'DIS', 'TMO', 'TIF', 'TWX',
       'TJX', 'TMK', 'TSS', 'TDG', 'RIG', 'FOXA', 'FOX', 'TYC', 'TSN',
       'USB', 'UDR', 'ULTA', 'UA', 'UNP', 'UAL', 'UNH', 'UPS', 'URI',
       'UTX', 'UHS', 'UNM', 'URBN', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN',
       'VZ', 'VRTX', 'VIAB', 'V', 'VNO', 'WMT', 'WBA', 'WM', 'WAT', 'WFC',
       'HCN', 'WU', 'WRK', 'WY', 'WHR', 'WFM', 'WMB', 'WLTW', 'WEC', 'WYN',
       'WYNN', 'XEL', 'XLNX', 'XL', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZION',
       'SPY']




