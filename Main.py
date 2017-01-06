import pandas as pd
import numpy as np
from Graham.Standard import Standardize as model


def run(sym):
    """

    :param sym: Enter the ticker symbol you want model data from
    :return:
    """
    try:
        data = model(sym).make_model()
        print(data)
        return data

    except:
        print('Error')

a = run('AMZN')
a.to_excel('DCF.xlsx')


working = ['ADS', 'AFL', 'AGN', 'AMZN', 'AON', 'BBY', 'BEN', 'BHI', 'BLL',
       'CL', 'CRM', 'CXO', 'D', 'DLPH', 'EBAY', 'ED', 'ETFC', 'EXPD',
       'FLS', 'GPC', 'GWW', 'HCP', 'HST', 'HUM', 'INTU', 'JEC', 'KHC',
       'LH', 'MMM', 'NFLX', 'NVDA', 'ORCL', 'TSLA']




