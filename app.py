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


ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


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
    data = {}
    the_html = ''
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
    freq = dflt['freq']
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
    # add asset ids if relevant to page
    df['asset id'] = df[df['Publish date'] != '0']['URL'].apply(
        lambda x: (re.search(r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    df['Avg. time'] = round(df['Engaged minutes'] / df['Visitors'], 3)
    df['Category'] = df['Section'].apply(
        lambda x: x.split('|')[0] if x != 0 else 'none'
    )
    df['Subcategory'] = df['Section'].apply(
        lambda x: x.split('|')[-1] if x != 0 else 'none'
    )
    df['asset id'] = df[df['Publish date'] != '0']['URL'].apply(
        lambda x: (re.search(r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    df['Title'].apply(
        lambda x: x.title().replace("’S", "’s ").replace("'S ", "'s ") if x != 0 else 'none'
    ) 
    # Filter df just for articles
    df_articles = df[df['asset id'] != 'none']

    # -- GET TOP ARTICLES BY PAGE VIEWS
    # sort by page views
    df_articles = df_articles.sort_values(by=['Views'], ascending=False)
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
        title = df[filter]['Title'].values[0]
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
    data = {'the_list': sorted(article_list, key=lambda k: k['Views'], reverse=True)[:10]}
    the_html += template('top_articles_by_pv.html', data=data)

    # GET TOP ARTICLES IN SECTIONS OPINION, LIVING, ARTS, OPINION
    sections = ['opinion', 'whatson', 'living', 'sports']
    for section in sections:
        filter = df_articles['Category'] == section
        records = df_articles[filter].head(3).to_dict(orient='record')
        for record in records:
            record['Title'] = record['Title'][:72] + (record['Title'][72:] and '...')
            mins = int(record['Avg. time'])
            seconds = int((record['Avg. time'] - mins) * 60)
            record['avg time'] = f'''{mins}:{seconds:02d}'''
            for item in device_cols + referral_cols:
                record[f'''{item}%'''] = u.pct(record[item], record['Views'])
            record['Returning vis.%'] = u.pct(record['Returning vis.'], record['Visitors'])
            temp = []
            referrers = [
                ('search', record['Search refs%']), ('direct', record['Direct refs%']),
                ('other', record['Other refs%']), ('internal', record['Internal refs%']),
                ('Tw', record['Tw refs%']), ('FB', record['Fb refs%'])
            ]
            for item in sorted(referrers, key=lambda x: x[1], reverse=True):
                if item[1] > 9:
                    temp.append(f'''{item[1]} {item[0]}''')
            temp[0] = f'''<b>{temp[0]}</b>'''
            record['Referrers report'] = ", ".join(temp)
        data = {'Category': section, 'the_list': sorted(records, key=lambda k: k['Views'], reverse=True)}
        the_html += template('top_articles_by_section.html', data=data)
        # pprint.pprint(article_list)
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
    # site = dflt['site']
    freq = dflt['freq']
    # period = dflt['defaults']['period']
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


def parse_site_csv(dflt):
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
        filename=dflt['defaults']['files']['site_csv'],
        folders=['data', dflt['freq']],
        cols_to_keep=c.var['site_cols_keep']
    )
    site = dflt['site']
    freq = dflt['freq']
    period = {'daily': 90, 'weekly': 13, 'monthly': 3}[freq]
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
        data[f"{item + ' vs rm%'}"] = u.vs_rm_pct(
            new[item].values[0], total[item].mean()
        )
    # ---COMPARE THIS PERIOD TO OTHERS
    if freq == 'weekly' or 'monthly':
        this_pv = df.tail(1)['Views'].values[0]
        total_count = len(list(df['Views'].values))
        period_pv = sorted(list(df.tail(period)['Views'].values), reverse=True)
        this_pv_period_rank = (period_pv.index(this_pv)) + 1
        all_pv = sorted(list(df['Views'].values), reverse=True)
        this_pv_all_rank = (all_pv.index(this_pv)) + 1
        data['Views rank'] = f'''Was the {ordinal(this_pv_period_rank)} best {freq.replace('ly', '').replace('dai', 'day')} in last {period}, {ordinal(this_pv_all_rank)} best in last {total_count}'''

    # Get period avg, so I can use for 'key changes'
    # in report. ie if a change is > 5% of rm
    data['Views rm'] = round(total['Views'].mean(), 0)
    # get percentages of key metrics
    for item in device_cols + referral_cols:
        # What's the ratio of this stat to latest period's views?
        data[f'''{item + '%'}'''] = u.pct(new[item].values[0], new['Views'].values[0])
        # difference between new stat and total avg stat
        data[f'''{item + ' diff vs rm'}'''] = new[item].values[0] - round(total[item].mean(), 0)
        # percentage of difference between new stat and total avg stat
        data[f'''{item + ' vs rm%'}'''] = u.vs_rm_pct(new[item].values[0], total[item].mean())

    # percentage of visitors who are returning
    data['Returning vis.%'] = u.pct(new['Returning vis.'].values[0], new['Visitors'].values[0])
    # percentage of difference between new 'Returninv vis.' and total avg
    data['Returning vis. vs rm%'] = u.vs_rm_pct(new['Returning vis.'].values[0], total['Returning vis.'].mean())
    # get avg time on site (in decimal format. Can covert to mm:ss in report)
    data['site time dec'] = round(data['Engaged minutes'] / data['Visitors'], 2)
    data['site time'] = f'''{int(data['site time dec'])}:{int(round((data['site time dec'] - int(data['site time dec']))*60,0))}'''
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
    # pprint.pprint(data)
    return template('site_highlights.html', data=data, site=site, freq=freq, period=period)


def parse_sections_csv(dflt):
    df = read_csv(
        filename=dflt['defaults']['files']['top_sections'],
        folders=['data', dflt['freq']],
        cols_to_keep=c.var['sections_cols_keep']
    )
    # MODIFY DATAFRAME
    views_sum = df['Views'].sum()
    visitors_sum = df['Visitors'].sum()
    # ret_visitors_sum = df['Returning vis.'].sum()
    search_sum = df['Search refs'].sum()
    internal_sum = df['Internal refs'].sum()
    social_sum = df['Social refs'].sum()
    direct_sum = df['Direct refs'].sum()
    other_sum = df['Other refs'].sum()
    df['PV / post'] = round(df['Views'] / df['Posts'], 0)
    df['Avg. Time'] = round(df['Engaged minutes'] / df['Visitors'], 3)
    # Create record, add to list
    the_list = []
    for record in df.head(20).to_dict(orient='record'):
        obj = {}
        obj['Section'] = record['Section']
        obj['Posts'] = record['Posts']
        obj['PV %'] = u.pct(record['Views'], views_sum)
        obj['PV / Post'] = int(record['PV / post'])
        obj['UV %'] = u.pct(record['Visitors'], visitors_sum)
        obj['Returning Vis%'] = u.pct(record['Returning vis.'], record['Visitors'])
        time = record['Avg. Time']
        mins = int(time)
        seconds = int(round((time - mins) * 60,0))
        obj['Avg. time'] = f'''{mins}:{seconds:02d}'''
        obj['Search %'] = u.pct(record['Search refs'], record['Views'])
        obj['Internal %'] = u.pct(record['Internal refs'], record['Views'])
        obj['Social %'] = u.pct(record['Social refs'], record['Views'])
        obj['Direct %'] = u.pct(record['Direct refs'], record['Views'])
        obj['Other %'] = u.pct(record['Other refs'], record['Views'])
        the_list.append(obj)
    pprint.pprint(the_list)
    return template('top_sections.html', data={'the_list': the_list})


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

site_stats = parse_site_csv(
    {
        'site': site,
        'freq': freq,
        'defaults': c.var[site][freq],
    }
)

top_sections = parse_sections_csv(
    {
        'site': site,
        'freq': freq,
        'defaults': c.var[site][freq],
    }
)

stuff = header + kpi + site_stats + top_articles + long_reads + top_sections + top_referrers + footer
u.write_file(stuff, f'''{site}_{freq}.html''', ['reports'])
