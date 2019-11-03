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

    print(df.dtypes)
    # remove any nbsp's in the column names **************!!!!!!!!!
    df.columns = [x.strip().replace('\xa0', '_') for x in df.columns]
    return df


def parse_site_csv(df, freq, period):
    key_metrics = ['Views', 'Visitors', 'New Posts', 'Engaged minutes', 'Social interactions']
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
    if freq == 'daily':
        # get day of week of each row,
        # so I can compare to other same days
        df['Date'] = pd.to_datetime(df['Date'])
        df['DayOfWeek'] = df['Date'].dt.day_name(),
    data = {}
    # get key metrics for LATEST PERIOD, vs TOTAL PERIOD
    new = df.tail(1)
    total = df.tail(period)
    for item in key_metrics:
        data[item] = new[item].values[0]
        # print(f'{item[0 ]} RM value ', total[item[1]].mean())
        data[f'''{item + ' vs rm%'}'''] = u.vs_rm_pct(
            new[item].values[0], total[item].mean()
        )

    # Get period avg, so I can use for 'key changes'
    # in report. ie if a change us > 5% of rm
    data['Views rm'] = round(total['Views'].mean(), 0)
    # get percentages of key metrics
    for item in device_cols + referral_cols:
        # What's the ratio of this stat to latest period's views?
        data[f'''{item + '%'}'''] = u.pct(new[item].values[0], new['Views'].values[0])
        # difference between new stat and total avg stat
        data[f'''{item + ' diff vs rm'}'''] = new[item].values[0] - round(total[item].mean(), 0)
        # percentage of difference between new stat and total avg stat
        data[f'''{item + ' vs rm%'}'''] = u.vs_rm_pct(new[item].values[0], total[item].mean())

    # percentage of difference between new 'Returninv vis.' and total avg
    data['Returning vis. vs rm%'] = u.vs_rm_pct(new['Returning vis.'].values[0], total['Returning vis.'].mean())
    # get avg time on site (in decimal format. Can covert to mm:ss in report)
    data['site time dec'] = round(data['Engaged minutes'] / data['Visitors'], 2)
    data['site time dec vs rm%'] = u.vs_rm_pct(
        data['site time dec'],
        total['Engaged minutes'].mean() / total['Visitors'].mean()
    )
    # produce devices breakdown report string
    devices = [
        ('mobile', data['Mobile views%']),
        ('desktop', data['Desktop views%']),
        ('tablet', data['Tablet views%'])
    ]
    temp = []
    for item in sorted(devices, key=lambda x: x[1], reverse=True):
        temp.append(f'''{item[1]} {item[0]}''')
    data['Devices report'] = ", ".join(temp)
    # produce views breakdown report string
    referrers = [
        ('social', data['Social refs%']),
        ('search', data['Search refs%']),
        ('internal', data['Internal refs%']),
        ('direct', data['Direct refs%']),
        ('other', data['Other refs%']),
    ]
    temp = []
    for item in sorted(referrers, key=lambda x: x[1], reverse=True):
        temp.append(f'''{item[1]} {item[0]}''')
    data['Referrers report'] = ", ".join(temp)
    # produce referral changes
    referral_changes = [
        ('search', data['Search refs diff vs rm']),
        ('internal', data['Internal refs diff vs rm']),
        ('direct', data['Direct refs diff vs rm']),
        ('other', data['Other refs diff vs rm']),
        ('FB', data['Fb refs diff vs rm']),
        ('Tw', data['Tw refs diff vs rm']),
    ]
    temp = []
    for item in sorted(referral_changes, key=lambda x: x[1], reverse=True):
        if abs(item[1]) > (0.01 * data['Views rm']):
            if item[1] < 0:
                temp.append(f'''<span style="color: red; font-weight: 700;">{(u.humanize(item[1]))}</span> {item[0]}''')
            else:
                temp.append(f'''<span style="color: grey; font-weight: 700;">{u.humanize(item[1])}</span> {item[0]}''')
    data['Referrers change report'] = ", ".join(temp)
    return data


def parse_pages_csv(df):
    key_metrics = ['Views', 'Visitors', 'Engaged minutes', 'Social interactions']
    device_cols = ['Desktop views', 'Mobile views', 'Tablet views']
    referral_cols = [
        'Search refs', 'Internal refs', 'Direct refs',
        'Social refs', 'Other refs', 'Fb refs', 'Tw refs'
    ]
    # ---- FIX DATAFRAME --------
    # fix any columns that may have float data types but should be integers
    for item in key_metrics + device_cols + referral_cols:
        df[item] = df[item].apply(lambda x: int(x))
    # ---- MODIFY DATAFRAME --------
    # sort on page views
    df = df.sort_values(by=['Views'], ascending=False)
    # add asset ids if relevant to page
    df['asset id'] = df[df['Publish date'] != '0']['URL'].apply(
        lambda x: (re.search(r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )

    # GET asset ids of top 30 articles
    # We need 30 because applying 'set' to a smaller list
    # tends to put some top articles beyond index of 10
    df_top = df[df['asset id'] != 'none'].head(30)
    # print(list(df_top['asset id'].values))
    # now creae unique set of those assset IDs
    top_articles = list(set(df_top['asset id'].values))
    data_top_articles = []
    # Now, create collection based on those asset IDs
    for asset in top_articles:
        obj = {}
        filter = df['asset id'] == asset
        obj['url'] = df[filter]['URL'].values[0]
        obj['asset id'] = df[filter]['asset id'].values[0]
        title = (df[filter]['Title'].values[0]).title().replace("'S ", "'s ")
        obj['title'] = title[:75] + (title[75:] and '..')
        obj['author'] = (df[filter]['Authors'].values[0]).title()
        obj['section'] = (df[filter]['Section'].values[0]).split('|')[-1]
        obj['date'] = df[filter]['Publish date'].values[0]
        for item in key_metrics:
            obj[item] = df[filter][item].sum()
        for item in device_cols + referral_cols:
            obj[item] = df[filter][item].sum()
            obj[f'''{item}%'''] = u.pct(obj[item], obj['Views'])
        time = round((obj['Engaged minutes'] / obj['Visitors']), 2)
        mins = int(time)
        seconds = int((time - mins) * 60)
        obj['avg time'] = f'''{mins}:{seconds:02d}'''
        obj['Returning vis.'] = df[filter]['Returning vis.'].sum()
        obj['Returning vis.%'] = u.pct(obj['Returning vis.'], obj['Visitors'])
        temp = [] 
        referrers = [
            ('search', obj['Search refs%']), ('direct', obj['Direct refs%']), 
            ('other', obj['Other refs%']), ('internal', obj['Internal refs%']), 
            ('Tw', obj['Tw refs%']), ('FB', obj['Fb refs%'])
        ]
        for item in sorted(referrers, key=lambda x: x[1], reverse=True):
            temp.append(f'''{item[1]} {item[0]}''')
        obj['Referrers report'] = ", ".join(temp)

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
        'articles': sorted(data_top_articles, key=lambda k: k['Views'], reverse=True)[:10],
        'hp': data_hp,
    }


# MAIN

# intialize string
report = ''
data = {}

# get command parameters
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
data['site'] = parse_site_csv(df, freq, c.var[freq]['period'])

df = read_parsely_csv(
    c.var[freq][site]['pages_csv'],
    ['data', freq],
    c.var['pages_cols_keep']
)
data['pages'] = parse_pages_csv(df)

pprint.pprint(data)

report_site = template(f'''{freq}.html''', site=data['site'], hp=data['pages']['hp'], articles=data['pages']['articles'], freq=freq, name=site)
u.write_file(report_site, f'''{site}_{freq}.html''', ['reports'])
