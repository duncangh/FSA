import os
import ExtractWorking
import pandas as pd
import numpy as np
import pickle
from DataViewer import DataView
import collections
pd.set_option('mode.chained_assignment', None)



class Financial:
    ERRORS = []

    def __init__(self, data, path):
        self.data = data
        self.path = path.replace("/extracted_data/", "/financials_data/")

        self.iterate_keys()

        self.parse_periodic()
        self.parse_balance()

    # Separate keys into balance and periodic
    def iterate_keys(self):
        """
        Parse the keys found in the data ordered dict.
        Break out the keys which are periodic vs those that are instantaneous
        """

        raw_keys = pd.Series(list(self.data['cal']['roles'].keys()))
        clean_keys = raw_keys[~raw_keys.str.contains('Comprehen')]
        clean_keys = clean_keys[~clean_keys.str.contains('Disclosure')]

        self.balance = clean_keys[clean_keys.str.contains('Balance')].values
        self.periodic = clean_keys[~clean_keys.str.contains('Balance')].values

    # Flatten Ordered Dictionary -- Used for Both Periodic and Balance Construction
    def flatten_dict(self, dictionary, parent_key='', sep='_'):
        items = []
        for k, v in dictionary.items():
            if isinstance(k, tuple):
                new_key = parent_key + sep + k[0] + sep + k[1] if parent_key else k
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
                items.extend(self.flatten_dict(v, nk, sep=sep).items())
            else:
                items.append((nk, v))
        return dict(items)

    # Extract Financial Data From All Balance Statements; Write Out as pkl to path
    def parse_balance(self):

        for data in self.balance:
            try:
                file_name = self.path + data + '.pkl'

                flat = self.flatten_dict(self.data['cal']['roles'][data]['tree'])
                df = pd.DataFrame.from_dict(flat, orient='index')

                # Extract Data From Known Positions
                df['Category'] = df.index
                df['Date'] = df.Category.apply(lambda x: x.split('_')[-1])
                df['Field'] = df.Category.apply(lambda x: x.split('_')[-2])

                # Drop Index
                df.reset_index(drop=True, inplace=True)
                df = df[['Field', 'Date', 0]]

                # Do what you gotta do
                df = df.groupby('Date')[['Field', 0]].apply(lambda x: x.set_index('Field')).unstack(0).T.reset_index(0,
                                                                                                                     drop=True).T
                df.to_pickle(file_name)

            except:
                self.ERRORS.append(data)

    # Attempt to extract periodic financial statements and write out as pickle
    def parse_periodic(self):

        for data in self.periodic:
            try:
                file_name = self.path + data + '.pkl'

                flat = self.flatten_dict(self.data['cal']['roles'][data]['tree'])

                periodic_df = pd.DataFrame.from_dict(flat, orient='index')

                # Refine periodic_df, process dates and construct period range
                refined_periodic = self.periodic_label_finder(periodic_df)
                # Pivot refined_periodic in order to match template of similar files
                final_periodic = self.periodic_format_construct(refined_periodic)

                final_periodic.to_pickle(file_name)

            except:
                self.ERRORS.append(data)

    # Refine periodic_df, process dates and construct period range
    def periodic_label_finder(self, periodic_df):
        periodic_df['Category'] = periodic_df.index
        periodic_df['Count'] = periodic_df.Category.apply(lambda x: len(x.split('_')[:-2]))

        high = periodic_df.Count.values.max()

        for i in range(high + 1):
            if i == 0:
                periodic_df['Parent'] = periodic_df.Category.apply(lambda x: x.split('_')[i])
            else:
                periodic_df['Child %i' % i] = periodic_df[periodic_df.Count > i].Category.apply(
                    lambda x: x.split('_')[i])

        # Find Date Range in periodic_df
        periodic_df['Start'] = pd.to_datetime(periodic_df['Category'].apply(lambda x: x.split('_')[-2]))
        periodic_df['End'] = pd.to_datetime(periodic_df['Category'].apply(lambda x: x.split('_')[-1]))

        # Calculate TimeDelta For Period
        periodic_df['TimeDelta'] = periodic_df['End'] - periodic_df['Start']
        periodic_df.reset_index(drop=True, inplace=True)

        # Forward fill levels where labels are missing
        periodic_df = periodic_df.fillna(method='ffill', axis=1)

        # Aesthetics
        periodic_df['Value'] = periodic_df[0].apply(self.convert_vals)  # Convert value column to float and rename
        periodic_df.drop(['Category', 0, 'Start', 'Count'], axis=1, inplace=True)

        return periodic_df

    # Pivot Periodic Data for Formatting
    def periodic_format_construct(self, refined_periodic):
        """
        ==============================================================
        :Parameter: DataFrame returned from self.periodic_label_finder

        :Returns: Pivot Table (regardless of depth)

        ===================================================
        Pivot Table Parameters:
                                columns : [End, TimeDelta]
                                index   : [Parent, Children]
                                values  : [Value]

        """

        # Combine Columns to eliminate levels
        refined_periodic['TimeDelta'] = refined_periodic['TimeDelta'].apply(
            lambda x: str(round(x.days / 90)) + ' Quarters')
        refined_periodic['End'] = refined_periodic['End'].apply(lambda x: x.strftime('%B-%Y'))
        refined_periodic['Period'] = refined_periodic['End'].str.cat(refined_periodic['TimeDelta'], sep=' ')

        del refined_periodic['TimeDelta'], refined_periodic['End']

        # Get rid of all columns except for the relevant labels
        refined_periodic = refined_periodic.iloc[:, -3:]

        columns = ['Period']
        values = 'Value'
        index = list(refined_periodic.columns[refined_periodic.columns.str.contains('Child')])

        # Make pivot, write to excel
        periodic_piv = refined_periodic.pivot_table(columns=columns, index=index, values=values)
        return periodic_piv

    # Helper Function to periodic_label_finder
    def convert_vals(self, x):
        try:
            return float(x)
        except:
            return np.NaN

