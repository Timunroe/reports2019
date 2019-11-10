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


def ordinal(n): return "%d%s" % (
    n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])

# TODO: Compare daily stats to same days of week for period, all.
# TODO: Fold in long reads func into pages parse func


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

def df_to_records(df):
    # convert a dataframe pages subset to list of dicts
    # for use in templates
    key_metrics = [
        'Views', 'Visitors', 'Engaged minutes',
        'Social interactions'
    ]
    device_cols = ['Desktop views', 'Mobile views', 'Tablet views']
    referral_cols = [
        'Search refs', 'Internal refs', 'Direct refs',
        'Social refs', 'Other refs', 'Fb refs', 'Tw refs'
    ]
    records = df.to_dict(orient='record')
    for record in records:
        record['Title'] = record['Title'].replace(
            '\'S ', '\'s ').replace('\'T ', '\'t ')
        record['Title'] = record['Title'][:72] + \
            (record['Title'][72:] and '...')
        for item in device_cols + referral_cols:
            record[f'''{item}%'''] = u.pct(record[item], record['Views'])
        record['Returning vis.%'] = u.pct(
            record['Returning vis.'], record['Visitors'])
        time = round((record['Avg. time']), 2)
        mins = int(time)
        seconds = int((time - mins) * 60)
        record['Avg. time formatted'] = f'''{mins}:{seconds:02d}'''
        # referrers string
        temp = []
        referrers = [
            ('search', record['Search refs%']
             ), ('direct', record['Direct refs%']),
            ('other', record['Other refs%']
             ), ('internal', record['Internal refs%']),
            ('Tw', record['Tw refs%']), ('FB', record['Fb refs%'])
        ]
        for item in sorted(referrers, key=lambda x: x[1], reverse=True):
            if item[1] > 9:
                temp.append(f'''{item[1]}% {item[0]}''')
        temp[0] = f'''<b>{temp[0]}</b>'''
        record['Referrers report'] = ", ".join(temp)
        # devices string
        temp = []
        devices_pv = [
            ('mobile', record['Mobile views%']
             ), ('desktop', record['Desktop views%']),
            ('tablet', record['Tablet views%']),
        ]
        for item in sorted(devices_pv, key=lambda x: x[1], reverse=True):
            if item[1] > 9:
                temp.append(f'''{item[1]}% {item[0]}''')
        temp[0] = f'''<b>{temp[0]}</b>'''
        record['Devices report'] = ", ".join(temp)
    return {
        'the_list': sorted(records, key=lambda k: k['Views'], reverse=True)
    }


def pages_parse(dflt):
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
    site = dflt['site']
    df = read_csv(
        filename=f'''{site}-pages.csv''',
        folders=['data', freq],
        cols_to_keep=dflt['config']['pages_cols_keep']
    )
    key_metrics = ['Views', 'Visitors',
                   'Engaged minutes', 'Social interactions']
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
    df['asset id'] = df['URL'].apply(
        lambda x: (re.search(
            r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    df['Title'] = df['Title'].apply(
        lambda x: x.title() if x != 0 else 'none'
    )
    # obits have Pub date and Asset ID, but Title == none
    # index pages have Title but Pub date == 0 and Asset ID == none
    # true article pages have title != none, Asset Id != none
    # Filter df just for articles
    df_articles_temp = df[(df['asset id'] != 'none') & (df['Title'] != 'none')]
    # sort by pub date for following aggregate functions
    print(df_articles_temp[df_articles_temp['Publish date'] == 0])
    df_articles_temp = df_articles_temp.sort_values(by=['Publish date'], ascending=False)
    # aggregate article data by asset ID
    aggregation_functions = {
        'URL': 'first',
        'Title': 'first',
        'Publish date': 'last',
        'Authors': 'first',
        'Section': 'first',
        'Tags': 'first',
        'Visitors': 'sum',
        'Views': 'sum',
        'Engaged minutes': 'sum',
        'New vis.': 'sum',
        'Returning vis.': 'sum',
        'Desktop views': 'sum',
        'Mobile views': 'sum',
        'Tablet views': 'sum',
        'Search refs': 'sum',
        'Internal refs': 'sum',
        'Other refs': 'sum',
        'Direct refs': 'sum',
        'Social refs': 'sum',
        'Fb refs': 'sum',
        'Tw refs': 'sum',
        'Social interactions': 'sum',
        'Fb interactions': 'sum',
        'Tw interactions': 'sum',
        'asset id': 'first',
    }
    df_articles = df_articles_temp.groupby(
        df_articles_temp['asset id']).aggregate(aggregation_functions)
    # ADD MORE COLUMNS NEEDED FOR ARTICLES
    df_articles['Avg. time'] = round(
        df_articles['Engaged minutes'] / df_articles['Visitors'], 3)
    df_articles['Category'] = df_articles['Section'].apply(
        lambda x: x.split('|')[0] if x != 0 else 'none'
    )
    df_articles['Subcategory'] = df_articles['Section'].apply(
        lambda x: x.split('|')[-1] if x != 0 else 'none'
    )
    # convert tags category to string if not already
    df_articles['Tags'] = df['Tags'].apply(
        lambda x: str(x) if x == 0 else x
    )
    # -- GET TOP ARTICLES BY PAGE VIEWS

    # sort by page views
    df_articles = df_articles.sort_values(by=['Views'], ascending=False)
    # CHANGE 10 IF MORE/FEWER TOP ARTICLES WANTED
    limit = {'daily': 7, 'weekly': 10, 'monthly': 10}[freq]
    top_articles = df_articles.head(limit).to_dict(orient='record')
    data = df_to_records(top_articles)
    the_html = template('top_articles_by_pv.html', data=data)
    # -- GET TOP ARTICLES IN SECTIONS OPINION, LIVING, ARTS, OPINION
    sections = ['whatson', 'living', 'sports']
    for section in sections:
        # CHANGE 3 IF DIFFERENT NUMBER OF ARTICLES WANTED
        section_pages = df_articles[df_articles['Tags'].str.contains(
            section)].head(3)
        data = df_to_records(section_pages)
        the_html += template('top_articles_by_section.html', data=data)
    opinion_pages = df_articles[
        (df_articles['Tags'].str.contains('opinion')) &
        (df_articles['Tags'].str.contains(
            'sports|living|whatson|subcategory:news', regex=True) == False)
    ].head(3)
    # handle top articles in with only opinion as category
    data = df_to_records(opinion_pages)
    the_html += template('top_articles_by_section.html', data=data)
    # SHOULD INSERT ARTICLES BY READ TIME HERE
    visitor_limit = 200
    df_articles = df_articles.sort_values(by=['Avg. time'], ascending=False)
    long_reads = df_articles[df_articles['Visitors'] > visitor_limit].head(5)
    data = df_to_records(long_reads)
    the_html += template('top_referrers.html', data=data)
    # -- GET HOME PAGE STATS
    url = dflt['config']['home'][site]
    df_hp = df[df['URL'] == url]
    # *** need to access site csv here
    df_site = read_csv(
        filename=f'''{site}-site-2019.csv''',
        folders=['data', freq],
        cols_to_keep=dflt['config']['site_cols_keep']
    )
    df_site = df_site.sort_values(by=['Date'], ascending=False)
    pv_total = df_site.tail(1)['Views'].values[0]
    time = round((df_hp['Engaged minutes'].values[0] /
                  df_hp['Visitors'].values[0]), 2)
    mins = int(time)
    seconds = int((time - mins) * 60)
    data_hp = {
        'avg time': f'''{mins}:{seconds:02d}''',
        'pv': df_hp['Views'].values[0],
        'pv vs total': u.pct(df_hp['Views'].values[0], pv_total),
        'uv': df_hp['Visitors'].values[0],
        'min': df_hp['Engaged minutes'].values[0],
        'returning uv%': u.pct(
            df_hp['Returning vis.'].values[0], df_hp['Visitors'].values[0]
            ),
        'mobile pv': df_hp['Mobile views'].values[0],
        'desktop pv': df_hp['Desktop views'].values[0],
        'tablet pv': df_hp['Tablet views'].values[0],
        'mobile pv%': u.pct(
            df_hp['Mobile views'].values[0], df_hp['Views'].values[0]
            ),
        'desktop pv%': u.pct(
            df_hp['Desktop views'].values[0], df_hp['Views'].values[0]
            ),
        'tablet pv%': u.pct(
            df_hp['Tablet views'].values[0], df_hp['Views'].values[0]
            ),
        'search pv%': u.pct(
            df_hp['Search refs'].values[0], df_hp['Views'].values[0]
            ),
        'direct pv%': u.pct(
            df_hp['Direct refs'].values[0], df_hp['Views'].values[0]
            ),
        'internal pv%': u.pct(
            df_hp['Internal refs'].values[0], df_hp['Views'].values[0]
            ),
        'social pv%': u.pct(
            df_hp['Social refs'].values[0], df_hp['Views'].values[0]
            ),
        'other pv%': u.pct(
            df_hp['Other refs'].values[0], df_hp['Views'].values[0]
            ),
    }
    the_html += template('home_page.html', data=data_hp,
                         inputs=c.var['inputs'][site][freq])
    return the_html


def top_referrers_parse(dflt):
    # pprint.pprint(df.head(10).to_dict(orient='record'))
    df = read_csv(
        filename=f'''{site}-referrers.csv''',
        folders=['data', freq],
        cols_to_keep=dflt['defaults']['referrers_cols_keep']
    )
    df_site = read_csv(
        filename=f'''{site}-site-2019.csv''',
        folders=['data', freq],
        cols_to_keep=dflt['defaults']['site_cols_keep']
    )
    # Sort DF so most recent item is first
    df_site = df_site.sort_values(by=['Date'], ascending=False)
    # Get PV total of latest period
    pv = df_site.head(1)['Views'].values[0]
    data = {
        'top_referrers': df.head(10).to_dict(orient='record'),
        'pv': pv,
    }
    the_html = template('top_referrers.html', data=data)
    return the_html


def site_parse(dflt):
    site = dflt['site']
    freq = dflt['freq']
    period = dflt['config'][freq]['period']
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
        folders=['data', freq],
        cols_to_keep=dflt['config']['site_cols_keep']
    )
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
        df['DayOfWeek'] = df['Date'].dt.day_name()

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
        data['Views rank'] = (
            f'''Was {ordinal(this_pv_period_rank)} best '''
            f'''{dflt['config'][freq]['term']} in last {period}, '''
            f'''{ordinal(this_pv_all_rank)} best in last {total_count}'''
        )

    # Get period avg, so I can use for 'key changes'
    # in report. ie if a change is > 5% of rm
    data['Views rm'] = round(total['Views'].mean(), 0)
    # get percentages of key metrics
    for item in device_cols + referral_cols:
        # What's the ratio of this stat to latest period's views?
        data[f'''{item + '%'}'''] = u.pct(new[item].values[0],
                                          new['Views'].values[0])
        # difference between new stat and total avg stat
        data[f'''{item + ' diff vs rm'}'''] = new[item].values[0] - \
            round(total[item].mean(), 0)
        # percentage of difference between new stat and total avg stat
        data[f'''{item + ' vs rm%'}'''] = u.vs_rm_pct(
            new[item].values[0], total[item].mean())

    # percentage of visitors who are returning
    data['Returning vis.%'] = u.pct(
        new['Returning vis.'].values[0], new['Visitors'].values[0])
    # percentage of difference between new 'Returninv vis.' and total avg
    data['Returning vis. vs rm%'] = u.vs_rm_pct(
        new['Returning vis.'].values[0], total['Returning vis.'].mean())
    # get avg time on site (in decimal format. Can covert to mm:ss in report)
    data['site time dec'] = round(
        data['Engaged minutes'] / data['Visitors'], 2)
    data['site time'] = (
        f'''{int(data['site time dec'])}:'''
        f'''{int(round((data['site time dec'] - int(data['site time dec']))*60,0))}'''
    )
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
        temp.append(f'''{item[1]}% {item[0]}''')
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
        temp.append(f'''{item[1]}% {item[0]}''')
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
                temp.append((
                    f'''<span style="color: #8B0000; font-weight: 700;">'''
                    f'''{(u.humanize(value=item[1]))}</span> {item[0]}'''
                ))
            else:
                temp.append((
                    f'''<span style="color: #006400; font-weight: 700;">'''
                    f'''{u.humanize(value=item[1], sign=True)}'''
                    f'''</span> {item[0]}'''
                    ))
    data['Referrers change report'] = ", ".join(temp)
    # pprint.pprint(data)
    return template(
        'site_highlights.html',
        data=data, site=site, freq=freq,
        period=period, term=dflt['config'][freq]['term'])


def parse_sections_csv(dflt):
    df = read_csv(
        filename=f'''{site}-sections.csv''',
        folders=['data', dflt['freq']],
        cols_to_keep=c.var['sections_cols_keep']
    )
    # MODIFY DATAFRAME
    views_sum = df['Views'].sum()
    visitors_sum = df['Visitors'].sum()
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
        obj['Returning Vis%'] = u.pct(
            record['Returning vis.'], record['Visitors'])
        time = record['Avg. Time']
        mins = int(time)
        seconds = int(round((time - mins) * 60, 0))
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
if (len(sys.argv) > 2
    and (sys.argv)[1] in ['daily', 'weekly', 'monthly']
    and (sys.argv)[2] in [
        'spectator', 'record', 'standard', 'examiner',
        'tribune', 'review', 'star'
        ]):
    freq = (sys.argv)[1]
    site = (sys.argv)[2]
else:
    print(
        "Requires 2 parameters:\n[daily/weekly/monthly]" +
        "\n[spectator/record/examiner/star]"
    )
    sys.exit()

# read in CSV, only keeping columns we want

header = template('header.html', site=site, freq=freq)
footer = template('footer.html')

site_stats = site_parse(
    {
        'site': site,
        'freq': freq,
        'config': c.var,
    }
)

top_articles = pages_parse(
    {
        'site': site,
        'freq': freq,
        'config': c.var,
    }
)


if freq != 'daily':

    kpi = template(
        'kpi.html',
        data={
            'site': site,
            'freq': freq,
            'input': c.var['inputs']
        }
    )

    top_referrers = top_referrers_parse(
        {
            'site': site,
            'freq': freq,
            'config': c.var,
        }
    )

    top_sections = parse_sections_csv(
        {
            'site': site,
            'freq': freq,
            'config': c.var,
        }
    )

    stuff = header + kpi + site_stats + top_articles + \
        top_sections + top_referrers + footer

else:

    stuff = header + site_stats + top_articles + footer


u.write_file(stuff, f'''{site}_{freq}.html''', ['reports'])
