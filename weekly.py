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


def parse_pages_csv(df):
    # ---- FIX DATAFRAME --------
    print(df.dtypes)
    df['Publish date'] = df['Publish date'].apply(lambda x: '0' if x == '' else x)
    # fix columns that have object(string) data types but should be integers
    for item in [
        'Mobile views', 'Tablet views', 'Search refs', 'Internal refs',
        'Other refs', 'Direct refs', 'Social refs', 'Fb refs', 'Tw refs',
        'Social interactions', 'Fb interactions', 'Tw interactions',
    ]:
        df[item] = df[item].apply(lambda x: 0 if x == '' else int(x.replace('.0', '')))
    # fix columns that have float data types but should be integers
    for item in [
        'Engaged minutes', 'Desktop views'
    ]:
        df[item] = df[item].apply(lambda x: int(x))
    # ---- MODIFY DATAFRAME --------
    # add asset ids if avilable
    df['asset id'] = df[df['Publish date'] != '0']['URL'].apply(
        lambda x: (re.search(r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    # get avg time
    df['avg time'] = round(df['Visitors'] / df['Engaged minutes'], 2)
    # sort on page views
    df = df.sort_values(by=['Views'], ascending=False)
    # GET asset ids of top 10 articles
    df_top = df[df['Publish date'] != '0'].head(30)
    # print(list(df_top['asset id'].values))
    top_articles = list(set(df_top['asset id'].values))
    data_top_articles = []
    # Now, with top 10 unique assets, add up any possible dupes
    for asset in top_articles:
        obj = {}
        filter = df['asset id'] == asset
        obj['url'] = df[filter]['URL'].values[0]
        obj['asset id'] = df[filter]['asset id'].values[0]
        obj['title'] = df[filter]['Title'].values[0]
        obj['author'] = df[filter]['Authors'].values[0]
        obj['section'] = df[filter]['Section'].values[0]
        obj['date'] = df[filter]['Publish date'].values[0]
        obj['pv'] = df[filter]['Views'].sum()
        obj['uv'] = df[filter]['Visitors'].sum()
        obj['min'] = df[filter]['Engaged minutes'].sum()
        time = round((obj['min'] / obj['uv']), 2)
        mins = int(time)
        seconds = int((time - mins) * 60)
        obj['avg time'] = f'''{mins}:{seconds:02d}'''
        obj['returning'] = df[filter]['Returning vis.'].sum()
        obj['desktop pv'] = df[filter]['Desktop views'].sum()
        obj['mobile pv'] = df[filter]['Mobile views'].sum()
        obj['tablet pv'] = df[filter]['Tablet views'].sum()
        obj['search refs'] = df[filter]['Search refs'].sum()
        obj['internal refs'] = df[filter]['Internal refs'].sum()
        obj['direct refs'] = df[filter]['Direct refs'].sum()
        obj['other refs'] = df[filter]['Other refs'].sum()
        obj['social refs'] = df[filter]['Social refs'].sum()
        obj['fb refs'] = df[filter]['Fb refs'].sum()
        obj['tw refs'] = df[filter]['Tw refs'].sum()
        obj['social int'] = df[filter]['Social interactions'].sum()
        data_top_articles.append(obj)

    df_hp = df[df['URL'] == 'https://www.thespec.com']
    time = round((df_hp['Engaged minutes'].values[0] / df_hp['Visitors'].values[0]), 2)
    mins = int(time)
    seconds = int((time - mins) * 60)
    data_hp = {
        'avg time': f'''{mins}:{seconds:02d}''',
        'pv': df_hp['Views'].values[0],
        'uv': df_hp['Visitors'].values[0],
        'min': df_hp['Engaged minutes'].values[0],
        'returning uv%': u.pct(df_hp['Returning vis.'].values[0], df_hp['Visitors'].values[0]),
        'mobile pv': df_hp['Mobile views'].values[0],
        'desktop pv': df_hp['Desktop views'].values[0],
        'tablet pv': df_hp['Tablet views'].values[0],
        'mobile pv%': u.pct(df_hp['Mobile views'].values[0], df_hp['Views'].values[0]),
        'desktop pv%': u.pct(df_hp['Desktop views'].values[0], df_hp['Views'].values[0]),
        'tablet pv%': u.pct(df_hp['Tablet views'].values[0], df_hp['Views'].values[0]),
        'search pv%': u.pct(df_hp['Search refs'].values[0], df_hp['Views'].values[0]),
        'direct pv%': u.pct(df_hp['Direct refs'].values[0], df_hp['Views'].values[0]),
        'internal pv%': u.pct(df_hp['Internal refs'].values[0], df_hp['Views'].values[0]),
        'social pv%': u.pct(df_hp['Social refs'].values[0], df_hp['Views'].values[0]),
        'other pv%': u.pct(df_hp['Other refs'].values[0], df_hp['Views'].values[0]),
    }
    return {
        'articles': sorted(data_top_articles, key=lambda k: k['pv'], reverse=True)[:10],
        'hp': data_hp,
    }


def parse_site_csv(df, period):
    # ---- FIX DATAFRAME --------
    # convert date column to datetime object
    # df['Date'] = pd.to_datetime(df['Date'])
    # get day of week from Date column, add it as another column
    # df['DayOfWeek'] = df['Date'].dt.day_name(),
    # fix columns that have float data types but should be integers
    for item in [
        'Desktop views', 'Search refs', 'Internal refs',
        'Other refs', 'Direct refs', 'Social refs',
        'Fb refs', 'Tw refs'
    ]:
        df[item] = df[item].apply(lambda x: int(x))
    # reverse sort on Date because that's how Pandas likes to roll
    df = df.sort_values(by=['Date'])
    # ---- MODIFY DATAFRAME --------
    data = {}
    # get key metrics for LATEST PERIOD, vs TOTAL PERIOD
    new = df.tail(1)
    total = df.tail(13)
    for item in [
        ('pv', 'Views'), ('uv', 'Visitors'), ('min', 'Engaged minutes'),
        ('posts', 'Posts')
    ]:
        data[item[0]] = new[item[1]].values[0]
        print(f'{item[0 ]} RM value ', total[item[1]].mean())
        data[f'''{item[0] + ' vs rm'}'''] = u.vs_rm_pct(new[item[1]].values[0], total[item[1]].mean())

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

    # data['site time dec'] = round(data['min'] / data['uv'], 2)
    return data


# [-- MAIN -----------]
# read in CSV, only keeping columns we want
df = read_parsely_csv(
    c.var['weekly']['site_archives_csv'],
    ['data', 'weekly'],
    c.var['site_cols_keep']
)
data['site'] = parse_site_csv(df, c.var['weekly']['period'])

df = read_parsely_csv(
    c.var['weekly']['pages_csv'],
    ['data', 'weekly'],
    c.var['pages_cols_keep']
)
data['pages'] = parse_pages_csv(df)


pprint.pprint(data)

# pprint.pprint(data)

# pprint.pprint(list(df_pages.columns.values))
# pprint.pprint(df_pages.dtypes)
# pprint.pprint(df_pages)
# pprint.pprint(df_site[0:2].to_csv(index=False))
