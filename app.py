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

# intialize string
report = ''
data = {}


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
            keep_default_na=False,
            na_values='0',
            usecols=cols_to_keep
        )
    else:
        df = pd.read_csv(
            path,
            keep_default_na=False,
            na_values='0',
        )
    # remove any nbsp's in the column names **************!!!!!!!!!
    df.columns = [x.strip().replace('\xa0', '_') for x in df.columns]
    return df


def parse_site_csv(df, freq, period):
    key_metrics = ['Views', 'Visitors', 'New Posts', 'Engaged minutes', 'Social interactions']
    device_cols = ['Desktop views', 'Mobile views', 'Tablet views']
    referral_cols


    # ---- FIX DATAFRAME --------
    # fix columns that may have float data types but should be integers

    for item in [
        'Desktop views', 'Mobile views', 'Tablet views', 'Search refs',
        'Internal refs', 'Other refs', 'Direct refs', 'Social refs',
        'Fb refs', 'Tw refs',
    ]:
        df[item] = df[item].apply(lambda x: int(x))
    # reverse sort on Date because that's how Pandas likes to roll
    # this means for latest data we'll pull 'last' or tail items
    df = df.sort_values(by=['Date'])
    # ---- MODIFY DATAFRAME --------
    if freq == 'daily':
        # get day of week of each row, 
        # so I can compare to same day of week
        df['Date'] = pd.to_datetime(df['Date'])
        df['DayOfWeek'] = df['Date'].dt.day_name(),
    data = {}
    # get key metrics for LATEST PERIOD, vs TOTAL PERIOD
    new = df.tail(1)
    total = df.tail(period)
    for item in [
        ('pv', 'Views'), ('uv', 'Visitors'), ('min', 'Engaged minutes'),
        ('posts', 'Posts')
    ]:
        data[item[0]] = new[item[1]].values[0]
        # print(f'{item[0 ]} RM value ', total[item[1]].mean())
        data[f'''{item[0] + ' vs rm'}'''] = u.vs_rm_pct(
            new[item[1]].values[0], total[item[1]].mean()
        )
    data['pv rm'] = round(total['Views'].mean(), 0)
    # get percentages of key metrics
    for item in [
        ('desktop pv', 'Desktop views', 'Views'),
        ('mobile pv', 'Mobile views', 'Views'),
        ('tablet pv', 'Tablet views', 'Views'),
        ('search pv', 'Search refs', 'Views'),
        ('internal pv', 'Internal refs', 'Views'),
        ('direct pv', 'Direct refs', 'Views'),
        ('social pv', 'Social refs', 'Views'),
        ('other pv', 'Other refs', 'Views'),
        ('fb pv', 'Fb refs', 'Views'),
        ('tw pv', 'Tw refs', 'Views'),
        ('returning uv', 'Returning vis.', 'Visitors')
    ]:
        # data[item[0]] =  int(round((df.tail(1)[item[1]].values[0] / data['pv']) * 100, 0))
        data[f'''{item[0] + ' diff vs rm'}'''] = new[item[1]].values[0] - new[item[2]].values[0]
        data[f'''{item[0] + '%'}'''] = u.pct(new[item[1]].values[0], new[item[2]].values[0])
        data[f'''{item[0] + ' vs rm'}'''] = u.vs_rm_pct(new[item[1]].values[0], total[item[1]].mean())
    # get avg time on site (in decimal format. Can covert to mm:ss in report)
    data['site time dec'] = round(data['min'] / data['uv'], 2)
    return data


# MAIN
if len(sys.argv) > 2 and (sys.argv)[1] in ['daily', 'weekly', 'monthly'] and (sys.argv)[2] \
        in ['spectator', 'record', 'niagara', 'standard', 'examiner', 'tribune', 'review', 'star']:
    freq = (sys.argv)[1]
    site = (sys.argv)[2]
else:
    print(
        "Requires 2 parameters:\n[daily/weekly/monthly]\n[spectator/record/niagara/examiner/star]")
    sys.exit()


# read in CSV, only keeping columns we want
df = read_parsely_csv(
    c.var[freq][site]['site_archives_csv'],
    ['data', freq],
    c.var['site_cols_keep']
)
data['site'] = parse_site_csv(df, c.var[freq]['period'])

df = read_parsely_csv(
    c.var['weekly']['pages_csv'],
    ['data', 'weekly'],
    c.var['pages_cols_keep']
)
data['pages'] = parse_pages_csv(df)


pprint.pprint(data)