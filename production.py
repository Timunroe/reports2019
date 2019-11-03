from bottle import template
import pandas as pd
# standard
import json
import pprint
import pathlib
import sys
import re
import datetime
# mine
import utils as u
import config as c

site_cols_keep = [
    'Date',
    'Posts',
    'Visitors',
    'Views',
    'Engaged minutes',
    'Social interactions',
    'Fb interactions',
    'Tw interactions',
    'Pi interactions',
    'Desktop views',
    'Mobile views',
    'Tablet views',
    'Search refs',
    'Internal refs',
    'Other refs',
    'Direct refs',
    'Social refs',
    'Fb refs',
    'Tw refs',
    'New vis.',
    'Views new vis.',
    'Avg. views new vis.',
    'Minutes New Vis.',
    'Avg. minutes new vis.',
    'Returning vis.',
    'Views ret. vis.',
    'Avg. views ret. vis.',
    'Minutes Ret. Vis.',
    'Avg. minutes ret. vis.',
]





def read_parsely_csv(filename, folders=None, cols_to_keep=None):
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


def parse_site_csv(df, file):
    key_metrics = ['Views', 'Visitors', 'Posts', 'Engaged minutes', 'Social interactions']
    device_cols = ['Desktop views', 'Mobile views', 'Tablet views']
    referral_cols = [
        'Search refs', 'Internal refs', 'Direct refs',
        'Social refs', 'Other refs', 'Fb refs', 'Tw refs'
    ]
    # ---- FIX DATAFRAME --------
    # fix any columns that may have float data types but should be integers
    for item in key_metrics + device_cols + referral_cols:
        df[item] = df[item].apply(lambda x: int(x))
    # reverse sort on Date because that's how Pandas likes to roll
    # this means for latest data we'll pull 'last' or tail items
    df = df.sort_values(by=['Date'])
    # ---- MODIFY DATAFRAME --------
    df['Date'] = pd.to_datetime(df['Date'])
    # print(df.dtypes)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    data = {}
    days = [
        'Monday', 'Tuesday', 'Wednesday', 
        'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    print(file)
    df_30 = df.tail(28)
    for day in days:
        new_posts = int(round(df_30[df_30['DayOfWeek'] == day]['Posts'].mean(), 0))
        views = int(round(df_30[df_30['DayOfWeek'] == day]['Views'].mean(), 0))
        visitors = int(round(df_30[df_30['DayOfWeek'] == day]['Visitors'].mean(), 0))
        print(f'''{day}: total posts: {new_posts} Views: {u.humanize(views, 0)} Visitors: {u.humanize(visitors, 0)}''')
    return data



for item in [
    'spectator_posts_local.csv', 
    'spectator_posts_primarypub.csv',
    'spectator_posts_total.csv'
]:

    df = read_parsely_csv(
        item,
        ['data', 'daily'],
        site_cols_keep,
    )
    data = parse_site_csv(df, item)
