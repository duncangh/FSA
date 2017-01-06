import pandas as pd
import numpy as np
import settings
import os
import ExtractWorking
import logs
import pickle
from DataViewer import DataView
import collections
from Graham.helpers import *




# Map fields
map_balance = {'Assets' : 'Assets Total',
 'LiabilitiesAndStockholdersEquity' : 'Stockholders Equity & Liabilities Total',
 'AssetsCurrent' : 'Assets Current Total',
       'DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent' : 'Assets Non-Current',
       'DefinedBenefitPlanNoncurrentAssetsForPlanBenefits' : 'Assets Non-Current',
        'Goodwill' : 'Assets Non-Current',
       'IntangibleAssetsNetExcludingGoodwill' : 'Assets Non-Current',
     'LongTermInvestments' : 'Assets Non-Current',
       'MarketableSecuritiesNoncurrent' : 'Assets Non-Current',
     'OtherAssetsNoncurrent' : 'Assets Non-Current',
       'PropertyPlantAndEquipmentNet' : 'Assets Non-Current',
     'AccountsReceivableNetCurrent' : 'Assets Current',
       'CashAndCashEquivalentsAtCarryingValue' : 'Assets Current',
     'InventoryNet' : 'Assets Current',
       'MarketableSecuritiesCurrent' : 'Assets Current',
     'OtherAssetsCurrent' : 'Assets Current',
       'AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment' : 'Drop',
       'PropertyPlantAndEquipmentGross' : 'Drop',
     'Liabilities' : 'Liabilities Total',
       'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest' : 'Stockholder Equity',
       'LiabilitiesCurrent' : 'Liabilities Current Total',
     'LongTermDebtNoncurrent' : 'Liabilities Non-Current',
       'OtherLiabilitiesNoncurrent' : 'Liabilities Non-Current',
       'PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent' : 'Liabilities Non-Current',
       'MinorityInterest' : 'Stockholder Equity',
     'StockholdersEquity' : 'Stockholder Equity Total',
       'AvailableForSaleSecuritiesNoncurrent' : 'Assets Non-Current',
       'AvailableForSaleSecuritiesCurrent' : 'Assets Current',
       'InvestmentsInAffiliatesSubsidiariesAssociatesAndJointVentures' : 'Assets Non-Current',
}
map_income = {'ComprehensiveIncomeNetOfTax': 'Continuing Ops',
 'ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest': 'Continuing Ops',
 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest': 'Continuing Ops',
 'CostOfRevenue': 'Revenue',
 'CostsAndExpenses': 'Operating Expense',
 'DisposalGroupNotDiscontinuedOperationGainLossOnDisposal': 'Extroadinary and Discont Ops',
 'EarningsPerShareBasic': 'Totals',
 'EarningsPerShareDiluted': 'Totals',
 'IncomeLossFromContinuingOperationsBeforeIncome': 'Continuing Ops',
 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest': 'Continuing Ops',
 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments': 'Continuing Ops',
 'IncomeTaxExpenseBenefit': 'Continuing Ops',
 'InterestAndDebtExpense': 'Continuing Ops',
 'InvestmentIncomeInterest': 'Continuing Ops',
 'NetIncomeLoss': 'Totals',
 'NetIncomeLossAttributableToNoncontrollingInterest': 'Continuing Ops',
 'NetIncomeLossAvailableToCommonStockholdersBasic': 'Totals',
 'NonoperatingIncomeExpense': 'Continuing Ops',
 'OperatingIncomeLoss': 'Operating Expense',
 'OtherComprehensiveIncomeAvailableForSaleSecuritiesAdjustmentNetOfTaxPeriodIncreaseDecrease': 'Continuing Ops',
 'OtherComprehensiveIncomeDefinedBenefitPlansAdjustmentNetOfTaxPeriodIncreaseDecrease': 'Continuing Ops',
 'OtherComprehensiveIncomeDerivativesQualifyingAsHedgesNetOfTaxPeriodIncreaseDecrease': 'Continuing Ops',
 'OtherComprehensiveIncomeForeignCurrencyTransactionAndTranslationAdjustmentNetOfTaxPeriodIncreaseDecrease': 'Continuing Ops',
 'OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecrease': 'Continuing Ops',
 'OtherNonoperatingIncome': 'Continuing Ops',
 'ProfitLoss': 'Revenue',
 'ResearchDevelopmentAndRelatedExpenses': 'Operating Expense',
 'SalesRevenueNet': 'Revenue',
 'SellingGeneralAndAdministrativeExpense': 'Operating Expense',
 'WeightedAverageNumberOfDilutedSharesOutstanding': 'Totals',
 'WeightedAverageNumberOfSharesOutstandingBasic': 'Totals',
 'OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax' : 'drop',
 'OtherComprehensiveIncomeLossDerivativesQualifyingAsHedgesNetOfTax' : 'drop',
 'OtherComprehensiveIncomeLossPensionAndOtherPostretirementBenefitPlansAdjustmentNetOfTax' : 'drop',
 'OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax' : 'drop',
 'OtherComprehensiveIncomeLossNetOfTax' : 'drop'}

# After Extracting All Financials, Aggregate
def get_all_income_statements(sym, map_income=map_income):
    files = inc_files(sym)
    frames = []
    for file in files:
        frame = pd.read_pickle(file)
        frame.index.name = None
        frames.append(frame)

    df = pd.concat(frames, axis=1)
    df.dropna(axis=0, thresh=12, inplace=True)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Field'}, inplace=True)

    df['Category'] = df.Field
    df.replace({'Category': map_income}, inplace=True)
    df = df[df['Category'] != 'drop']

    df = df.set_index(['Category', 'Field']).sort_index()

    df = df / 1000000

    sym = files[0].split('/')[-5]
    path = '/Users/duncangh/Google Drive/Finance/Financial Statements/%s Income Statements.csv' % sym
    df.to_csv(path)
    return df


def get_all_balance_sheets(sym, map_balance=map_balance):
    files = get_files(sym)
    frames = []
    for file in files:
        frame = pd.read_pickle(file).iloc[:, :3]
        frame.set_index('index', inplace=True)
        frames.append(frame)

    df = pd.concat(frames, axis=1)
    df.dropna(axis=0, thresh=12, inplace=True)
    df['Category'] = df.index
    df.replace({'Category' : map_balance}, inplace=True)
    df.reset_index(inplace=True)
    df = df[df['Category'] != 'Drop']
    df = df.set_index(['Category', 'index']).sort_index()
    df = df / 1000000
    sym = files[0].split('/')[-5]
    path = '/Users/duncangh/Google Drive/Finance/Financial Statements/%s Balance Sheets.csv' % sym
    df.to_csv(path)
    return df


# get_all_balance_sheets(files, map_balance)
# get_all_income_statements(files, map_income)
