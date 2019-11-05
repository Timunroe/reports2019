from bottle import template
import pandas as pd
# standard
import json
import pprint
import pathlib
import sys
import re
import datetime
import math
# mine
import utils as u
import config as c
import manual as m


ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])


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


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def top_articles_parse(dflt):
    # deflt -> dict
    '''
        'site': site,
        'freq': freq,
        'defaults': c.var[site][freq]
    '''
    # get needed dataframes
    # parse needed dataframes
    # call template with data
    # return html
    site = dflt['site']
    freq = dflt['freq']
    period = dflt['defaults']['period']
    df = read_csv(
        filename=dflt['defaults']['files']['pages_csv'],
        folders=['data', freq],
        cols_to_keep=c.var['pages_cols_keep']
    )
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
    # Filter df just for articles
    df_articles = df[df['asset id'] != 'none']
    # We need 30 because applying 'set' to a smaller list
    # tends to put some top articles beyond index of 10
    top_articles = list(set(df_articles.head(30)['asset id'].values))
    article_list = []
    # Now, create collection based on those asset IDs
    for asset in top_articles:
        obj = {}
        filter = df['asset id'] == asset
        obj['url'] = df[filter]['URL'].values[0]
        obj['asset id'] = df[filter]['asset id'].values[0]
        title = (df[filter]['Title'].values[0]).title().replace("’S", "’s ").replace("'S ", "'s ")
        obj['title'] = title[:72] + (title[72:] and '...')
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
            if item[1] > 9:
                temp.append(f'''{item[1]} {item[0]}''')
        temp[0] = f'''<b>{temp[0]}</b>'''
        obj['Referrers report'] = ", ".join(temp)
        article_list.append(obj)
    data = {'article_list': sorted(article_list, key=lambda k: k['Views'], reverse=True)[:10]}
    the_html = template('top_articles_by_pv.html', data=data)
    return the_html


def top_referrers_parse(dflt):
    # pprint.pprint(df.head(10).to_dict(orient='record'))
    df = read_csv(
        filename=dflt['defaults']['files']['referrers'],
        folders=['data', freq],
        cols_to_keep=c.var['referrers_cols_keep']
    )
    df_pv = read_csv(
        filename=dflt['pv'],
        folders=['data', freq],
        cols_to_keep=c.var['site_cols_keep']
    )
    # Sort DF so most recent item is first
    df_pv = df_pv.sort_values(by=['Date'], ascending=False)
    # Get PV total of latest period
    pv = df_pv.head(1)['Views'].values[0]
    data = {
        'top_referrers': df.head(10).to_dict(orient='record'),
        'pv': pv,
    }
    the_html = template('top_referrers.html', data=data)
    return the_html


def long_reads_parse(dflt):
    # read in pages csv, add 'avg time' column, sort on that
    key_metrics = ['Views', 'Visitors', 'Engaged minutes', 'Social interactions']
    device_cols = ['Desktop views', 'Mobile views', 'Tablet views']
    referral_cols = [
        'Search refs', 'Internal refs', 'Direct refs',
        'Social refs', 'Other refs', 'Fb refs', 'Tw refs'
    ]
    site = dflt['site']
    freq = dflt['freq']
    period = dflt['defaults']['period']
    df = read_csv(
        filename=dflt['defaults']['files']['long_reads_csv'],
        folders=['data', freq],
        cols_to_keep=c.var['pages_cols_keep']
    )
    df['asset id'] = df[df['Publish date'] != '0']['URL'].apply(
        lambda x: (re.search(r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    df['Avg. time'] = round(df['Engaged minutes'] / df['Visitors'], 3)
    df_articles = df[df['asset id'] != 'none']    
    df_articles = df_articles.sort_values(by=['Avg. time'], ascending=False)
    the_list = []
    # Now, create collection based on those asset IDs
    for article in df_articles[df_articles['Visitors'] > 300].head(5).to_dict(orient='record'):
        obj = {}
        obj['url'] = article['URL']
        obj['asset id'] = article['asset id']
        title = article['Title'].title().replace("’S ", "’s ")
        obj['title'] = title[:72] + (title[72:] and '...')
        obj['author'] = article['Authors'].title()
        obj['section'] = article['Section'].split('|')[-1]
        obj['date'] = article['Publish date']
        for item in key_metrics:
            obj[item] = article[item]
        for item in device_cols + referral_cols:
            obj[item] = article[item]
            obj[f'''{item}%'''] = u.pct(obj[item], obj['Views'])
        obj['Returning vis.%'] = u.pct(article['Returning vis.'], article['Visitors'])
        time = article['Avg. time']
        mins = int(time)
        seconds = int(round((time - mins) * 60,0))
        obj['avg time'] = f'''{mins}:{seconds:02d}'''
        the_list.append(obj)
        temp = [] 
        referrers = [
            ('search', obj['Search refs%']), ('direct', obj['Direct refs%']), 
            ('other', obj['Other refs%']), ('internal', obj['Internal refs%']), 
            ('Tw', obj['Tw refs%']), ('FB', obj['Fb refs%'])
        ]
        for item in sorted(referrers, key=lambda x: x[1], reverse=True):
            if item[1] > 9:
                temp.append(f'''{item[1]} {item[0]}''')
        obj['Referrers report'] = ", ".join(temp)


    return template('long_reads.html', data={'the_list': the_list})


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
'''
df_site = read_parsely_csv(
    c.var[freq][site]['site_archives_csv'],
    ['data', freq],
    c.var['site_cols_keep']
)
data['site'] = parse_site_csv(df_site, freq, c.var[freq]['period'])

df_pages = read_parsely_csv(
    c.var[freq][site]['pages_csv'],
    ['data', freq],
    c.var['pages_cols_keep']
)
data['pages'] = parse_pages_csv(df_pages, data['site'])
hp = data['pages']['hp'].update(m.var[site][freq])

df_referrers = read_parsely_csv(
    c.var[freq][site]['referrers'],
    ['data', freq]
)
top_referrers = parse_referrers_csv(df_referrers)

df_long_reads = read_parsely_csv(
    c.var[freq][site]['long_reads'],
    ['data', freq]
)
top_long_reads = parse_long_reads_csv(df_long_reads)
'''

header = template('header.html', site=site, freq=freq)
footer = template('footer.html')

long_reads = long_reads_parse(
    {
        'site': site,
        'freq': freq,
        'defaults': c.var[site][freq]
    }
)

if freq != 'daily':
    kpi = template(
        'kpi.html',
        data={
            'site': site,
            # 'freq': freq,
            'input': m.var[site][freq]
        }
    )
else:
    kpi = ''

top_articles = top_articles_parse(
    {
        'site': site,
        'freq': freq,
        'defaults': c.var[site][freq]
    }
)

top_referrers = top_referrers_parse(
    {
        'site': site,
        'freq': freq,
        'defaults': c.var[site][freq],
        'pv': c.var[site][freq]['files']['site_csv']
    }
)

stuff = header + kpi + top_articles + long_reads + top_referrers + footer
u.write_file(stuff, f'''{site}_{freq}.html''', ['reports'])
