from bottle import template
import pandas as pd
# standard
# import json
import pprint
import pathlib
import sys
import re
# import datetime
import math
# mine
import utils as u
import config as c

# compare Saturday, Sundays in terms of overall traffic, social media refs, # of postsalso # of posts
# using daily site stats
# todo: breakout social traffic, see if any trends
# compare to weekly PV as %, so not influeneced by good/bad week.
# this much harder ... assign week No.s? or maybe say 'last 3'
# applies to both Saturdays and weeks. 


def read_csv(filename, folders=None, cols_to_keep=None):
    if folders:
        if not isinstance(folders, list):
            print("Folders parameter MUST be a list!")
            sys.exit()
        p = pathlib.Path.cwd().joinpath(*folders)
    else:
        p = pathlib.Path.cwd()
    path = p.joinpath(filename)
    if cols_to_keep:
        df = pd.read_csv(
            path,
            na_values=['(NA)'],
            usecols=cols_to_keep
        ).fillna(0)
    else:
        df = pd.read_csv(
            path,
            na_values=['(NA)'],
        ).fillna(0)

    # print(df.dtypes)
    # remove any nbsp's in the column names **************!!!!!!!!!
    df.columns = [x.strip().replace('\xa0', '_') for x in df.columns]
    return df


def site_parse(site):
    key_metrics = [
        'Views',
        'Visitors',
        'New Posts',
        'Engaged minutes',
        'Social interactions'
    ]
    device_cols = [
        'Desktop views', 'Mobile views', 'Tablet views'
    ]
    referral_cols = [
        'Search refs', 'Internal refs', 'Direct refs',
        'Social refs', 'Other refs', 'Fb refs', 'Tw refs'
    ]
    df = read_csv(
        filename=f'''{site}-site-2019.csv''',
        folders=['data', 'daily'],
        cols_to_keep=c.var['site_cols_keep']
    )
    # ---- FIX DATAFRAME --------
    # fix any columns that may have float data types but should be integers
    for item in key_metrics + device_cols + referral_cols:
        df[item] = df[item].apply(lambda x: int(x))
    # reverse sort on Date because that's how Pandas likes to roll
    # this means for latest data we'll pull 'last' or tail items
    df = df.sort_values(by=['Date'])
    # ---- MODIFY DATAFRAME --------
    # get day of week of each row,
    # so I can compare to other same days
    df['Date'] = pd.to_datetime(df['Date'])
    df['DayOfWeek'] = df['Date'].dt.day_name()
    # get a list of all x day's pages views, sorted.
    # then get index of this period's page views int that list, that's the rank.
    # export to CSV for testing-validation
    df.to_csv('site-test.csv')
    data = {}
    for day in ['Monday', 'Wednesday', 'Saturday', 'Sunday']:
        df_temp = df.iloc[-21:]
        data[f'''{day}PV_3weeks'''] = df_temp[df_temp['DayOfWeek'] == day]['Views'].mean()
        df_temp = df.iloc[-105: -21]
        data[f'''{day}PV_12weeks'''] = df_temp[df_temp['DayOfWeek'] == day]['Views'].mean()
        df_temp = df.iloc[-189: -105]
        data[f'''{day}PV_24weeks'''] = df_temp[df_temp['DayOfWeek'] == day]['Views'].mean()
    return data


# --[ MAIN ]---------

sites = ['spectator', 'record', 'standard', 'review', 'tribune', 'examiner']
days = ['Monday', 'Wednesday', 'Saturday', 'Sunday']
data = {}
for site in sites:
    data[f'''{site}'''] = site_parse(site)
pprint.pprint(data)

report = f'''
                Spec |  Rec  |  Stnd |  Rev  |  Trib |  Exam
----------------------------------------------------------------
'''
for day in days:
    for num in [3, 12, 24]:
        report += f'''{day[:3]} PV ({num})'''
        for site in sites:
            if num == 3:
                report += f''' | {(u.humanize(data[site][(day + 'PV_' + str(num) + 'weeks')])):>6}'''
            else:
                report += f''' | {(u.pct_diff(data[site][day + 'PV_3weeks'], data[site][(day + 'PV_' + str(num) + 'weeks')])):>5}%'''
        report += '\n'
    report += '----------------------------------------------------------------\n'
print(report)