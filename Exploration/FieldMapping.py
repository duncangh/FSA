import os
import pandas as pd
import numpy as np
import pickle
import collections
from Graham.Aggregation import Aggregate
pd.set_option('mode.chained_assignment', None)
pd.set_option('display.width', 1500)


symbols = np.array(os.listdir('/Users/duncangh/PycharmProjects/FSA/data/data/')[1:])

def cash_flows_fields(symbols=symbols):
    fields = []
    for sym in symbols:
        try:
            fields.extend(Aggregate(sym).cash_flows.index.values)
        except:
            pass
    field = pd.Series(fields)
    field_vc = field.value_counts()
    field_vc.to_frame().to_csv('Cash Fields.csv')
    print('Cash Done')

def balance_fields(symbols=symbols):
    fields = []
    for sym in symbols:
        try:
            fields.extend(Aggregate(sym).balance_sheet.index.values)
        except:
            pass

    field = pd.Series(fields)
    field_vc = field.value_counts()
    field_vc.to_frame().to_csv('Balance Fields.csv')
    print('Balance Done')

def income_fields(symbols=symbols):
    fields = []
    for sym in symbols:
        try:
            fields.extend(Aggregate(sym).income_statement.index.values)
        except:
            pass

    field = pd.Series(fields)
    field_vc = field.value_counts()
    field_vc.to_frame().to_csv('Income Fields.csv')
    print('Income Done')

# cash_flows_fields()
# balance_fields()
# income_fields()


df = pd.read_csv('/Users/duncangh/PycharmProjects/FSA/Exploration/Master Fields.csv').iloc[:, 1:]



xbrl = pd.read_excel('/Users/duncangh/PycharmProjects/FSA/XBRL Labels.xlsx', skiprows=1)[['elementName', 'balanceType', 'definition']]





class Standardize:
    def __init__(self, sym):
        self.symbol = sym
        self.statements = Aggregate(sym).statements

        self.balance = self.statements[0] / 10 ** 6
        self.income = self.statements[1] / 10 ** 6
        self.cash = self.statements[2] / 10 ** 6

        self.fcfe = self.free_cash_flow_equity()

    def standard_balance(self):
        """
         _____________
        | Assets:           Liabilities
         -------------       Current:
        | Current:
        |
        |   Cash                A/P
        |   A/R                 CPLTD
        |   Inventory           Other
        |   Other
        |
        | Non-Current:       Non-Current:
        |
        |   PP&E                Notes Payable
        |   Other               Other



        """

        self.balance.index[self.balance.index.str.contains('Current')].tolist()

        return 0

    def standard_income(self):
        return 0

    def standard_cash(self):
        return 0

    def change_nwc(self):
        """
        Calculate Change in Net Working Capital. There are two main ways to do this:

            1. From The Statement of Cash Flows
            2. From The Balance Sheet
        """
        if 'AssetsCurrent' in self.balance.index:
            net = self.balance.loc['AssetsCurrent'] - self.balance.loc['LiabilitiesCurrent']
        else:
            try:
                net = (self.balance.loc['Assets'] - self.balance.loc['PropertyPlantAndEquipmentNet']) - (self.balance.loc['Liabilities'] - self.balance.loc['DebtAndCapitalLeaseObligations'])
            except:
                print("No Change NWC For this stock")

        self.chg_wc = net - net.shift(1)

        return self.chg_wc.fillna(0)

    def CapEx(self):
        self.capex = self.cash.loc[self.cash.index[self.cash.index.str.contains('PropertyPlantAndE')]]

        if self.capex.empty:
            return 0
        else:
            self.capex = self.capex.loc[self.capex.index.values[0]]
            return self.capex.fillna(0)

    def debt_cash(self):
        issued = self.cash.loc[
            self.cash.index[(self.cash.index.str.contains('Debt')) & (self.cash.index.str.contains('Iss'))]]
        if not issued.empty:
            issued = issued.loc[issued.index[0]].fillna(0)

        payments = self.cash.loc[
            self.cash.index[(self.cash.index.str.contains('Debt')) & (self.cash.index.str.contains('Repay'))]]
        if not payments.empty:
            payments = payments.loc[payments.index[0]].fillna(0)

        if payments.empty:
            return issued

        elif issued.empty:
            return payments

        else:
            return (issued - payments).fillna(0)

    def DeprAmort(self):
        DA = self.cash.loc[
            self.cash.index[(self.cash.index.str.contains('Depre')) | (self.cash.index.str.contains('Amort'))]]
        if not DA.empty:

            return DA.loc[DA.index.values[0]].fillna(0)
        else:
            return 0

    def interest_expense(self):
        # Handle all known cases of interest expense
        int_exp = self.income.loc[self.income.index[(self.income.index.str.contains('Interest'))
                                                    & (~self.income.index.str.contains('Minor'))
                                                    & (~self.income.index.str.contains('controll'))
                                                    & (~self.income.index.str.contains('Before'))
                                                    & (~self.income.index.str.contains('Gain'))
                                                    & (~self.income.index.str.contains('TotalRevenues'))
                                                    & (~self.income.index.str.contains('Investment'))
                                                    & (~self.income.index.str.contains('Nonopera'))
                                                    & (~self.income.index.str.contains('Income'))].values[0]]

        if not int_exp.empty:
            return int_exp.fillna(0)
        else:
            return 0

    def free_cash_flow_equity(self):
        """
        FCFe = NI + D/A - ∆ nwc - CapEx  + Net Debt
        """

        try:
            NI = self.income.loc['NetIncomeLoss'].fillna(0)
        except:
            NI = self.cash.loc['NetIncomeLoss'].fillna(0)
            if NI.empty:
                NI = self.income.loc[self.income.index[self.income.index.str.contains('NetIncome')].values[0]].fillna(0)

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        net_debt = self.debt_cash()
        if net_debt.empty:
            net_debt = 0

        NIDA = ((NI + DA).fillna(0) + net_debt).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (NIDA - nwcap)

    def free_cash_flow_firm(self):
        """
        FCFf = EBIT + Interest Expense + D/A - ∆ nwc - CapEx
        """

        try:
            EBIT = self.income.loc['OperatingIncomeLoss'].fillna(0)
        except:
            EBIT = self.income.loc[self.income.index[self.income.index.str.contains('OperatingIncome')]].fillna(0)
            if EBIT.empty:
                try:
                    EBIT = self.income.loc['NetIncomeLoss'] + self.income.loc['IncomeTaxExpenseBenefit'] + self.interest_expense()
                except:
                    pass

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        int_exp = self.interest_expense()

        EBITDA = ((EBIT + DA).fillna(0) + int_exp).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (EBITDA - nwcap)


    def weighted_average_cost_of_capital(self):
        """
        Total Capital = BV(equity) + BV(debt)
        Book Value of Equity = Assets - Liabilities
        Book Value of Debt = (Assets - Equity) - Non-Interest Bearing Obligations

        Equity Cost = Rrf + ß(Rm - Rrf)
        Cost of Debt = Interest Expense / Book Value of Debt

        Weight of Equity = BV Equity / Total Capital
        Weight of Debt = BV of Debt / Total Capital

        WACC = (WeightofEquity * CostofEquity) + (WeightofDebt * CostofDebt)

        :return: WACC
        """


