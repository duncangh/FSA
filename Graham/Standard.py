import os
import pandas as pd
import numpy as np
import pickle
import collections
try:
    from Graham.Aggregation import Aggregate
except:
    from Aggregation import Aggregate

pd.set_option('mode.chained_assignment', None)
pd.set_option('display.width', 1500)


class Standardize:
    def __init__(self, sym, rf=1.5):
        self.symbol = sym
        self.statements = Aggregate(sym).statements
        self.risk_free = rf

        self.balance = self.statements[0] / 10 ** 6
        self.income = self.statements[1] / 10 ** 6
        self.cash = self.statements[2] / 10 ** 6

        self.current_assets = np.array(['IncomeTaxesReceivable', 'OtherAssetsCurrent',
                                        'DeferredTaxAssetsLiabilitiesNetCurrent', 'RegulatoryAssetsCurrent',
                                        'InventoryNet', 'OtherPrepaidExpenseCurrent',
                                        'InventoryFinishedGoods', 'ReceivablesNetCurrent', 'PrepaidTaxes',
                                        'InventoryWorkInProcess', 'PrepaidExpenseCurrent',
                                        'DerivativeAssetsCurrent',
                                        'AssetsOfDisposalGroupIncludingDiscontinuedOperationCurrent',
                                        'InventoryRawMaterialsAndSupplies',
                                        'CashAndCashEquivalentsAtCarryingValue', 'ShortTermInvestments',
                                        'CapitalLeasedAssetsGross',
                                        'RestrictedCashAndCashEquivalentsAtCarryingValue',
                                        'RestrictedCashAndInvestmentsCurrent',
                                        'CashEquivalentsAtCarryingValue', 'MarketableSecuritiesCurrent',
                                        'MarketableSecuritiesCurrent', 'NotesAndLoansReceivableNetCurrent',
                                        'AccountsReceivableNetCurrent',
                                        'AvailableForSaleSecuritiesDebtSecuritiesCurrent',
                                        'AvailableForSaleSecuritiesDebtSecuritiesCurrent',
                                        'AvailableForSaleSecuritiesCurrent',
                                        'PrepaidExpenseAndOtherAssetsCurrent'])

        self.current_liabilities = np.array(
            ['CostsInExcessOfBillingsOnUncompletedContractsOrProgramsExpectedToBeCollectedWithinOneYear',
             'LiabilitiesOfDisposalGroupIncludingDiscontinuedOperationCurrent',
             'OtherLiabilitiesCurrent', 'DueToRelatedPartiesCurrent',
             'RegulatoryLiabilityCurrent',
             'DeferredTaxLiabilitiesCurrent', 'AccountsPayableCurrent',
             'DebtCurrent', 'AccountsPayableAndAccruedLiabilitiesCurrent',
             'AccruedLiabilitiesCurrent', 'EmployeeRelatedLiabilitiesCurrent', 'CustomerAdvancesCurrent',
             'DeferredRevenueCurrent', 'DeferredRevenueAndCreditsCurrent',
             'DerivativeLiabilitiesCurrent', 'OtherShortTermBorrowings',
             'BankOverdrafts', 'CommercialPaper', 'TaxesPayableCurrent',
             'ShortTermBankLoansAndNotesPayable',
             'CapitalLeaseObligationsCurrent', 'ShortTermBorrowings',
             'LongTermDebtCurrent'])

        self.interest_bearing = np.array(['DueToRelatedPartiesCurrent', 'DebtCurrent',
                                          'OtherShortTermBorrowings', 'BankOverdrafts', 'CommercialPaper',
                                          'ShortTermBankLoansAndNotesPayable',
                                          'CapitalLeaseObligationsCurrent', 'ShortTermBorrowings',
                                          'LongTermDebtCurrent', 'LongTermDebtAndCapitalLeaseObligations',
                                          'CapitalLeaseObligationsNoncurrent', 'OtherLongTermDebtNoncurrent',
                                          'LongTermDebtAndCapitalLeaseObligationsCurrent',
                                          'LongTermDebtNoncurrent', 'SeniorLongTermNotes',
                                          'ConvertibleLongTermNotesPayable'],
                                         dtype='<U45')

        self.fcfe = self.free_cash_flow_equity()

    def change_nwc(self):
        if 'AssetsCurrent' and 'LiabilitiesCurrent' in self.balance.index:
            net = self.balance.loc['AssetsCurrent'] - self.balance.loc['LiabilitiesCurrent']

        else:
            net = (self.balance[self.balance.index.isin(self.current_assets)].sum()).fillna(0) - (
            self.balance[self.balance.index.isin(self.current_liabilities)].sum()).fillna(0)

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
            return DA.max()
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

    def ebit(self):
        """
        Calculate the EBIT

        """
        try:
            EBIT = self.income.loc['OperatingIncomeLoss'].fillna(0)
        except:
            EBIT = self.income.loc[self.income.index[self.income.index.str.contains('OperatingIncome')]].fillna(0)
            if EBIT.empty:
                try:
                    EBIT = self.income.loc['NetIncomeLoss'] + self.income.loc[
                        'IncomeTaxExpenseBenefit'] + self.interest_expense()
                    EBIT = EBIT.fillna(0)
                except:
                    pass

        return EBIT

    def free_cash_flow_equity(self):
        """
        FCFe = NI + D/A - ∆ nwc - CapEx  + Net Debt
        """

        try:
            NI = self.income.loc['NetIncomeLoss'].fillna(0)
        except:
            try:
                NI = self.cash.loc['NetIncomeLoss'].fillna(0)
            except:
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

        EBIT = self.ebit()

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        int_exp = self.interest_expense()

        EBITDA = ((EBIT + DA).fillna(0) + int_exp).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (EBITDA - nwcap)

    def book_value_debt(self):
        return self.balance[self.balance.index.isin(self.interest_bearing)].sum()

    def book_value_equity(self):
        """
        Book Value of Equity = Value of Stockholders Equity

        """
        return self.balance.loc['StockholdersEquity'].fillna(0)

    def cost_debt(self, debt):
        """
        Calculate the cost of debt Using
            1. amount of debt
            2. interest expense
            3. Tax Rate if possible

        """
        interest = self.interest_expense()
        earnings_before_taxes = (self.ebit() - interest).fillna(0)
        tax_rate = self.income.loc['IncomeTaxExpenseBenefit'].fillna(0) / earnings_before_taxes

        interest_rate = (interest / debt) * 100

        if 0 < tax_rate.mean() < 1:
            return (interest_rate * (1 - tax_rate)).fillna(0)
        else:
            return interest_rate.fillna(0)

    def cost_equity(self):
        """
        Rrf + ß(Rm - Rrf)

        MRP is assumed to be 4.5%
        """
        beta = pd.read_pickle('/Users/duncangh/PycharmProjects/FSA/Graham/Beta.Pkl')['SPY'].abs()
        beta.index = beta.index.astype(str)
        return self.risk_free + beta * (4.5 - self.risk_free)

    def weighted_average_cost_of_capital(self):
        """
        Total Capital = BV(equity) + BV(debt)
        Book Value of Equity = Assets - Liabilities
        Book Value of Debt = (Assets - Equity) - Non-Interest Bearing Obligations

        Equity Cost = Rrf + ß(Rm - Rrf)
        Cost of Debt = (Interest Expense / Book Value of Debt) * (1 - MarginalTaxRate)

        Weight of Equity = BV Equity / Total Capital
        Weight of Debt = BV of Debt / Total Capital

        WACC = (WeightofEquity * CostofEquity) + (WeightofDebt * CostofDebt)
        WACC = rD(1 - Tc) * (D / V) + rE * (E / V)

        :return: WACC
        """
        book_value_debt = self.book_value_debt()
        book_value_equity = self.book_value_equity()

        total_capital = book_value_debt + book_value_equity

        weight_debt = book_value_debt / total_capital
        weight_equity = book_value_equity / total_capital

        cost_debt = self.cost_debt(book_value_debt)
        cost_equity = self.cost_equity()

        wacc = (weight_debt * cost_debt) + (weight_equity * cost_equity)

        return weight_debt, weight_equity, cost_debt, cost_equity, wacc

    def make_model(self):
        wd, we, cd, ce, wacc = self.weighted_average_cost_of_capital()
        fcfe = self.free_cash_flow_equity()
        fcff = self.free_cash_flow_firm()
        model = pd.DataFrame({'FCFF': fcff, 'FCFE': fcfe})
        model = model.assign(Cost_Equity=ce, Cost_Debt=cd, Weight_Equity=we, Weight_Debt=wd, WACC=wacc)
        model = model.fillna(method='bfill')
        return model



























class ov9Standardize:
    def __init__(self, sym, rf=1.5):
        self.symbol = sym
        self.statements = Aggregate(sym).statements
        self.risk_free = rf

        self.balance = self.statements[0] / 10 ** 6
        self.income = self.statements[1] / 10 ** 6
        self.cash = self.statements[2] / 10 ** 6

        self.fcfe = self.free_cash_flow_equity()

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
                net = (self.balance.loc['Assets'] - self.balance.loc['PropertyPlantAndEquipmentNet']) - (
                self.balance.loc['Liabilities'] - self.balance.loc['DebtAndCapitalLeaseObligations'])
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
            return DA.max()
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

    def ebit(self):
        """
        Calculate the EBIT

        """
        try:
            EBIT = self.income.loc['OperatingIncomeLoss'].fillna(0)
        except:
            EBIT = self.income.loc[self.income.index[self.income.index.str.contains('OperatingIncome')]].fillna(0)
            if EBIT.empty:
                try:
                    EBIT = self.income.loc['NetIncomeLoss'] + self.income.loc[
                        'IncomeTaxExpenseBenefit'] + self.interest_expense()
                    EBIT = EBIT.fillna(0)
                except:
                    pass

        return EBIT

    def free_cash_flow_equity(self):
        """
        FCFe = NI + D/A - ∆ nwc - CapEx  + Net Debt
        """

        try:
            NI = self.income.loc['NetIncomeLoss'].fillna(0)
        except:
            try:
                NI = self.cash.loc['NetIncomeLoss'].fillna(0)
            except:
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

        EBIT = self.ebit()

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        int_exp = self.interest_expense()

        EBITDA = ((EBIT + DA).fillna(0) + int_exp).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (EBITDA - nwcap)

    def book_value_debt(self):
        """
        Book Value of Debt = (Assets - Equity) - Non-Interest Bearing Obligations

        Use this method to perform the above calculation. Should be robust to natural
        Variety in the names of common Non-Interest Bearing Obligations.

        """

        total_liabilities = self.balance.loc['LiabilitiesAndStockholdersEquity'].fillna(0) - self.balance.loc[
            'StockholdersEquity'].fillna(0)
        if 'AccountsPayableCurrent' in self.balance.index:
            return total_liabilities - self.balance.loc['AccountsPayableCurrent'].fillna(0)

        else:
            return total_liabilities.fillna(0)

    def book_value_equity(self):
        """
        Book Value of Equity = Value of Stockholders Equity

        """
        return self.balance.loc['StockholdersEquity'].fillna(0)

    def cost_debt(self, debt):
        """
        Calculate the cost of debt Using
            1. amount of debt
            2. interest expense
            3. Tax Rate if possible

        """
        interest = self.interest_expense()
        earnings_before_taxes = (self.ebit() - interest).fillna(0)
        tax_rate = self.income.loc['IncomeTaxExpenseBenefit'].fillna(0) / earnings_before_taxes

        interest_rate = (interest / debt) * 100

        if 0 < tax_rate.mean() < 1:
            return (interest_rate * (1 - tax_rate)).fillna(0)
        else:
            return interest_rate.fillna(0)

    def cost_equity(self):
        """
        Rrf + ß(Rm - Rrf)

        MRP is assumed to be 4.5%
        """
        beta = pd.read_pickle('/Users/duncangh/PycharmProjects/FSA/Graham/Beta.Pkl')[self.symbol].abs()
        beta.index = beta.index.astype(str)
        return self.risk_free + beta * (4.5 - self.risk_free)

    def weighted_average_cost_of_capital(self):
        """
        Total Capital = BV(equity) + BV(debt)
        Book Value of Equity = Assets - Liabilities
        Book Value of Debt = (Assets - Equity) - Non-Interest Bearing Obligations

        Equity Cost = Rrf + ß(Rm - Rrf)
        Cost of Debt = (Interest Expense / Book Value of Debt) * (1 - MarginalTaxRate)

        Weight of Equity = BV Equity / Total Capital
        Weight of Debt = BV of Debt / Total Capital

        WACC = (WeightofEquity * CostofEquity) + (WeightofDebt * CostofDebt)
        WACC = rD(1 - Tc) * (D / V) + rE * (E / V)

        :return: WACC
        """
        book_value_debt = self.book_value_debt()
        book_value_equity = self.book_value_equity()

        total_capital = book_value_debt + book_value_equity

        weight_debt = book_value_debt / total_capital
        weight_equity = book_value_equity / total_capital

        cost_debt = self.cost_debt(book_value_debt)
        cost_equity = self.cost_equity()

        wacc = (weight_debt * cost_debt) + (weight_equity * cost_equity)

        return weight_debt, weight_equity, cost_debt, cost_equity, wacc

    def make_model(self):
        wd, we, cd, ce, wacc = self.weighted_average_cost_of_capital()
        fcfe = self.free_cash_flow_equity()
        fcff = self.free_cash_flow_firm()
        model = pd.DataFrame({'FCFF': fcff, 'FCFE': fcfe})
        model = model.assign(Cost_Equity=ce, Cost_Debt=cd, Weight_Equity=we, Weight_Debt=wd, WACC=wacc)
        model = model.fillna(method='bfill')
        return model

class v49Standardize:
    def __init__(self, sym, rf=.015):
        self.symbol = sym
        self.statements = Aggregate(sym).statements
        self.risk_free = rf

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

    def ebit(self):
        """
        Calculate the EBIT

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

        return EBIT

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

        EBIT = self.ebit()

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        int_exp = self.interest_expense()

        EBITDA = ((EBIT + DA).fillna(0) + int_exp).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (EBITDA - nwcap)


    def book_value_debt(self):
        """
        Book Value of Debt = (Assets - Equity) - Non-Interest Bearing Obligations

        Use this method to perform the above calculation. Should be robust to natural
        Variety in the names of common Non-Interest Bearing Obligations.

        """

        total_liabilities = self.balance.loc['LiabilitiesAndStockholdersEquity'].fillna(0) - self.loc['StockholdersEquity'].fillna(0)
        if 'AccountsPayableCurrent' in self.balance.index:
            return total_liabilities - self.balance.loc['AccountsPayableCurrent'].fillna(0)

        else:
            return total_liabilities

    def book_value_equity(self):
        """
        Book Value of Equity = Value of Stockholders Equity

        """
        if 'CommonStockValue' in self.balance.index:
            return self.balance.loc['CommonStockValue'].fillna(0)
        else:
            return self.balance.loc['StockholdersEquity'].fillna(0)

    def cost_debt(self, debt):
        """
        Calculate the cost of debt Using
            1. amount of debt
            2. interest expense
            3. Tax Rate if possible

        """
        interest = self.interest_expense()
        earnings_before_taxes = self.ebit() - interest
        tax_rate = self.income.loc['IncomeTaxExpenseBenefit'] / earnings_before_taxes

        interest_rate = interest / debt

        if 0 < tax_rate < 1:
            return interest_rate * (1 - tax_rate)
        else:
            return interest_rate

    def cost_equity(self):
        """
        Rrf + ß(Rm - Rrf)

        MRP is assumed to be 4.5%
        """
        beta = pd.read_pickle('/Users/duncangh/PycharmProjects/FSA/Graham/Beta.Pkl')[self.symbol].mean()

        return self.risk_free + beta(.045 - self.risk_free)




    def weighted_average_cost_of_capital(self):
        """
        Total Capital = BV(equity) + BV(debt)
        Book Value of Equity = Assets - Liabilities
        Book Value of Debt = (Assets - Equity) - Non-Interest Bearing Obligations

        Equity Cost = Rrf + ß(Rm - Rrf)
        Cost of Debt = (Interest Expense / Book Value of Debt) * (1 - MarginalTaxRate)

        Weight of Equity = BV Equity / Total Capital
        Weight of Debt = BV of Debt / Total Capital

        WACC = (WeightofEquity * CostofEquity) + (WeightofDebt * CostofDebt)
        WACC = rD(1 - Tc) * (D / V) + rE * (E / V)

        :return: WACC
        """
        book_value_debt = self.book_value_debt()
        book_value_equity = self.book_value_equity()

        total_capital = book_value_debt + book_value_equity

        weight_debt = book_value_debt / total_capital
        weight_equity = book_value_equity / total_capital

        cost_debt = self.cost_debt(book_value_debt)
        cost_equity = self.cost_equity()

        return (weight_debt * cost_debt) + (weight_equity * cost_equity)
class v42Standardize:
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

        net = self.balance.loc['AssetsCurrent'] - self.balance.loc['LiabilitiesCurrent']
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
            NI = self.income.loc[self.income.index[self.income.index.str.contains('NetIncome')].values[0]].fillna(0)
            if NI.empty:
                NI = self.income.loc[self.income.index[self.income.index.str.contains('OperatingIncome')]].fillna(0)
                NI = NI.loc[NI.index.values[0]]

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
                EBIT = self.income.loc[self.income.index[self.income.index.str.contains('OperatingIncome')]].fillna(0)
                EBIT = EBIT.loc[EBIT.index.values[0]]

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        int_exp = self.interest_expense()

        EBITDA = ((EBIT + DA).fillna(0) + int_exp).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (EBITDA - nwcap)





class v35Standardize:
    def __init__(self, sym):
        self.symbol = sym
        self.statements = Aggregate(sym).statements

        self.balance = self.statements[0]
        self.income = self.statements[1]
        self.cash = self.statements[2]

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

        net = self.balance.loc['AssetsCurrent'] - self.balance.loc['LiabilitiesCurrent']
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

    def free_cash_flow_equity(self):
        """
        FCFe = NI + D/A - ∆ nwc - CapEx  + Net Debt
        """

        try:
            NI = self.income.loc['NetIncomeLoss'].fillna(0)
        except:
            NI = self.income.loc[self.income.index[self.income.index.str.contains('NetIncome')]].fillna(0)
            if NI.empty:
                NI = self.income.loc[self.income.index[self.income.index.str.contains('OperatingIncome')]].fillna(0)
                NI = NI.loc[NI.index.values[0]]

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        net_debt = self.debt_cash()
        if net_debt.empty:
            net_debt = 0

        NIDA = ((NI + DA).fillna(0) + net_debt).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (NIDA - nwcap)





























class v2Standardize:
    def __init__(self, sym):
        self.symbol = sym
        self.statements = Aggregate(sym).statements

        self.balance = self.statements[0]
        self.income = self.statements[1]
        self.cash = self.statements[2]

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

        net = self.balance.loc['AssetsCurrent'] - self.balance.loc['LiabilitiesCurrent']
        self.chg_wc = net - net.shift(1)

        return self.chg_wc.fillna(0)

    def CapEx(self):
        self.capex = self.cash.loc[self.cash.index[self.cash.index.str.contains('PropertyPlantAndE')]]
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
            return DA.fillna(0)
        else:
            return 0

    def free_cash_flow_equity(self):
        """
        FCFe = NI + D/A - ∆ nwc - CapEx  + Net Debt
        """

        try:
            NI = self.income.loc['NetIncomeLoss'].fillna(0)
        except:
            NI = self.income.loc[self.income.index[self.income.index.str.contains('NetIncome')]].fillna(0)

        DA = self.DeprAmort()
        nwc_chg = self.change_nwc()
        capex = self.CapEx()

        net_debt = self.debt_cash()

        NIDA = ((NI + DA).fillna(0) + net_debt).fillna(0)
        nwcap = (nwc_chg + capex).fillna(0)
        return (NIDA - nwcap)
class oldStandardize:

    def __init__(self, sym):
        self.symbol = sym
        self.statements = Aggregate(sym).statements

        self.balance = self.statements[0]
        self.income = self.statements[1]
        self.cash = self.statements[2]



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


        net = self.balance.loc['AssetsCurrent'] - self.balance.loc['LiabilitiesCurrent']
        self.chg_wc = net - net.shift(1)

        return self.chg_wc

    def CapEx(self):
        self.capex = self.cash.loc[self.cash.index[self.cash.index.str.contains('PropertyPlantAndE')]]
        return self.capex

    def debt_cash(self):
        issued = self.cash.loc[self.cash.index[(self.cash.index.str.contains('Debt')) & (self.cash.index.str.contains('Iss'))]]
        payments = self.cash.loc[self.cash.index[(self.cash.index.str.contains('Debt')) & (self.cash.index.str.contains('Repay'))]]


        if payments.empty:
            return issued

        elif issued.empty:
            return payments

        else:
            return issued - payments

    def DeprAmort(self):
        try:
            return self.cash.loc[self.cash.index[(self.cash.index.str.contains('Depre')) | (self.cash.index.str.contains('Amort'))]]
        except:
            return 0

    def free_cash_flow_equity(self):
        """
        FCFe = NI + D/A - ∆ nwc - CapEx  + Net Debt
        """

        NI = self.income.loc['NetIncomeLoss']
        DA = self.DeprAmort()
        nwc_chg = self.chg_wc()
        capex = self.CapEx()
        net_debt = self.debt_cash()

        return NI + DA - nwc_chg - capex + net_debt