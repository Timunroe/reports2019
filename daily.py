from bottle import template
import pandas as pd
# standard
import json
import pprint
import pathlib
import sys
import re
# mine
import utils as u
import config as c


'''
Read yesterday's file ...
Download yesterday's site stats, drop in daily folder

simple bash line will append 2nd line of day file to 
master file:
gsed -n '2p' spectator-site-yesterday-thespec-com-any.csv >> spectator_site_2019.csv

What safeguards to make sure it's the right file?
filename = spectator-site-yesterday-thespec-com-any.csv
> get date of stats, compare with last date in master file?
Need to read csv files to compare the data

Pages info:
home page traffic: day's total, day's total vs 90-day avg, 
  day's total vs last 13 same weekdays, overdirect, direct vs 90 day avg

Top story by search, internal, direct, facebook, twitter, other

SITE HIGHLIGHTS:
Page views: 767K, -1.0% vs rolling avg., +/-% last 12 XXXdays.
Breakdown %: 20 social, 17 search, 35 internal, 20 direct, 4 other
Devices %: 48 mobile, 39 desktop, 13 tablet

Referral changes vs average: Search 7K, Other 3.9K, FB 2.2K, Direct -8.2K, Internal -13.6K

Visitors: 199K, +3.0% vs avg., +/-% vs previous 12 XXXdays.
Minutes: 473K, -5.0% vs avg, +/-% vs previous 12 XXXdays.
*Average is 13-week rolling average.

SITE INSIGHTS:
Home page PV: 
% Desktop page views vs rolling avg
% Mobile page views +/-% vs rolling avg
% of page views to non-articles
% of page views to content older than 7 days
(need to get reference date - latest in site csv)


TOP POSTS: By Referrers
SEARCH: Top story by page views
headline 
X % of total -- X clicks | asset #
-----
SOCIAL: Top story by page views
headline 
X % of total -- X clicks | asset #
-----
INTERNAL: Top story by page views
headline 
X % of total -- X clicks | asset #
-----
OTHER: Top story by page views
headline 
X % of total -- X clicks | asset #
-----
DIRECT: Top story by page views
headline 
X % of total -- X clicks | asset #
-----

week day - 

'''


def t(n, mn=None, sign=False):
    # convert number to text for formatting
    if sign:
        if n > 0:
            symbol = '+'
        else:
            symbol = ''
    else:
        symbol = ''
    if mn:
        if n > mn:
            return f'''**{re.sub('.0$', '', symbol + str(n))}**'''
        else:
            return f'''<span style="color: red">**{re.sub('.0$', '', symbol + str(n))}**</span>'''
    else:
        return re.sub('.0$', '', symbol + str(n))


def sign(text):
    if not text.startswith('-'):
        text = '+' + text
    # convert number to text with plus/minus sign
    return text


# handy helpers
newline = '\n'
dbline = '\n\n'

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
    return df


def massage_site_csv(df):
    # remove any nbsp's in the column names
    df.columns = [x.strip().replace('\xa0', '_') for x in df.columns]
    # convert date column to datetime object
    df['Date'] = pd.to_datetime(df['Date'])
    # get day of week from Date column, add it as another column
    df['DayOfWeek'] = df['Date'].dt.day_name(),
    # fix columns that have float data types but should be integers
    for item in [
        'Desktop views', 'Search refs', 'Internal refs', 
        'Other refs', 'Direct refs', 'Social refs', 
        'Fb refs', 'Tw refs'
    ]:
        df[item] = df[item].apply(lambda x: int(x))
    # reverse sort on Date because that's how Pandas likes to roll
    df = df.sort_values(by=['Date'])
    return df


def massage_pages_csv(df):
    # remove any nbsp's in the column names
    df.columns = [x.strip().replace('\xa0', '_') for x in df.columns]
    # convert date column to datetime object
    df['Date'] = pd.to_datetime(df['Date'])
    # get day of week from Date column, add it as another column
    df['DayOfWeek'] = df['Date'].dt.day_name(),
    # fix columns that have float data types but should be integers
    for item in [
        'Desktop views', 'Search refs', 'Internal refs', 
        'Other refs', 'Direct refs', 'Social refs', 
        'Fb refs', 'Tw refs'
    ]:
        df[item] = df[item].apply(lambda x: int(x))
    # reverse sort on Date because that's how Pandas likes to roll
    df = df.sort_values(by=['Date'])
    return df


def parse_site_csv(df, period):
    data = {}
    # get site stats from site dataframe
    # get key metrics
    for item in [('pv', 'Views'), ('uv', 'Visitors'), ('m', 'Engaged minutes')]:
        data[item[0]] = df.tail(1)[item[1]].values[0]
    # get percentages of key metrics
    for item in [
        ('Desktop%', 'Desktop views'), 
        ('Mobile%', 'Mobile views'), 
        ('Tablet%', 'Tablet views'),
        ('Search%', 'Search refs'),
        ('Internal%', 'Internal refs'),
        ('Direct%', 'Direct refs'),
        ('Social%', 'Social refs'),
        ('Other%', 'Other refs'),
        ('Fb%', 'Fb refs'),
        ('Tw%', 'Tw refs'),
    ]:
        data[item[0]] = int(round((df.tail(1)[item[1]].values[0] / data['pv']) * 100, 0))

    data['Returning%'] = int(round(
        (df.tail(1)['Returning vis.'] / data['uv']) * 100, 0
    ))
    # get changes in key metrics vs 90-day period
    return data


# read in CSV, only keeping columns we want
df = read_parsely_csv(
    c.var['daily']['site_csv'], 
    ['data', 'daily'], 
    c.var['site_cols_keep']
)
df_site = massage_site_csv(df)
data['site'] = parse_site_csv(df_site, c.var['daily']['period'])

pprint.pprint(data)

# pprint.pprint(list(df_site.columns.values))
# pprint.pprint(df_site.dtypes)
# pprint.pprint(df_site[0:2].to_csv(index=False))
