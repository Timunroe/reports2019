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

# 1. take csv of author's posts, group on article ID.
# 2. take csv of last clicks, group on article ID
# 3. take author article IDs, find matches in last clicks csv.

params = {
    'sites': {
        'spectator': {
            'name': 'spectator',
            'authors': [
                'Benedetti', 'Berton', 'Buist', 'Canning', 'Clairmont', 
                'Clarke', 'Convery', 'Coward', 'Dreschel', 'Dyer', 
                'Fragomeni', 'Frketich', 'Furster', 'Galambos', 'Gardner', 
                'Gray', 'Grover', 'Haggo', 'Hogue', 'Howard', 'Hunter', 'Kemeny',
                'Little', 'MacKay', 'Mahoney', 'McKay', 'McNeil', 'Miller', 'Milton', 
                'Moore', 'Moro', 'Nadler', 'Nolan', 'O\'Reilly', 'Paddon', 'Pecoskie', 
                'Pike', 'Radley', 'Reilly', 'Rennison', 'Renwald', 
                'Rockingham', 'Schramayr', 'Shkimba', 'Smith', 'Sommerfeld', 
                'Stevens', 'Turnevicius', 'Van Dongen', 'Wells', 'Wilson', 'Yokoyama', 
                'Cohn', 'Mallick', 'Teitel', 'Menon', 'Tesher', 'Donovan', 'Potter', 'Burman', 
                'Walkom', 'Hebert', 'Delacourt', 'Scoffield', 'Hepburn', 'Salutin', 'Charlebois', 
                'Howe'
            ]
        },
        'record': {
            'name': 'record',
            'authors': [
                'Monteiro', 'Davis', 'Paul', 'Booth', 'Outhit',
                'Thompson', 'Jackson', 'Mercer', 'Desmond', 'Rubinoff',
                'Pender', 'Latif', 'D\'Amato', 'Weidner', 'Hicks',
                'Hill', 'Brown', 'Bryson', 'DeGroot', 'Hobson', 'Milloy',
                'Mills', 'Thoman', 'Bielak', 'Stevens', 'Taylor', 'Andrews', 
                'Walneck', 'Mangalaseril', 'CBrown', 'Edwards'
            ]
        },
        'niagara': {
            'name': 'niagara',
            'authors': [
                'Benner', 'Dube', 'Franke', 'Langley', 'Law',
                'Sawchuk', 'Spiteri', 'Walter', 'Tymczyszyn',
                'LaFleche', 'Jocsak', 'Johnson'
            ]
        },
        'examiner': {
            'name': 'examiner',
            'authors': [
                'Kovach', 'Nyznik', 'Bain', 'Davies', 'Skarstedt', 
                'Anderson', 'Arnold', 'Barrie', 'Campbell', 'Clysdale',
                'Culley', 'Dornan', 'Elson', 'Ganley', 'Gardiner', 'Gordon',
                'Harrison', 'Hickey', 'Jones', 'McConnell', 'Monkman',
                'O\'Grady', 'Peeters', 'Peterman', 'Saitz', 'Savage',
                'Taylor', 'Thompson', 'Vandonk', 'Watson'
            ]
        },
    }
}

authors_cols = [
    "URL",
    "Title",
    "Publish date",
    "Authors",
    "Section",
    "Tags",
    "Visitors",
    "Views",
    "Engaged minutes",
    "New vis.",
    "Returning vis.",
    "Views new vis.",
    "Views ret. vis.",
    "Minutes New Vis.",
    "Minutes Ret. Vis.",
    "Desktop views",
    "Mobile views",
    "Tablet views",
    "Search refs",
    "Internal refs",
    "Other refs",
    "Direct refs",
    "Social refs",
    "Fb refs",
    "Tw refs",
    "Social interactions",
    "Fb interactions",
    "Tw interactions"
]

clicks_cols = [
    "Post Page Url",
    "Title",
    "Last 3 Clicks",
    "Last Clicks"
]


def read_csv(filename, folders=None, cols_to_keep=None, tabs=False):
    if folders:
        if not isinstance(folders, list):
            print("Folders parameter MUST be a list!")
            sys.exit()
        p = pathlib.Path.cwd().joinpath(*folders)
    else:
        p = pathlib.Path.cwd()
    path = p.joinpath(filename)
    if cols_to_keep:
        if tabs:
            df = pd.read_csv(
                path,
                na_values=['(NA)'],
                usecols=cols_to_keep,
                sep='\t',
                encoding='UTF-16'
            ).fillna(0)
        else:
            df = pd.read_csv(
                path,
                na_values=['(NA)'],
                usecols=cols_to_keep,
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


def authors_parse(fn, name, site_name):
    df = read_csv(
        filename=fn,
        folders=['data', 'authors'],
        cols_to_keep=authors_cols
    )
    key_metrics = [
        'Views',
        'Visitors',
        'Engaged minutes',
        'Social interactions'
    ]
    device_cols = ['Desktop views', 'Mobile views', 'Tablet views']
    referral_cols = [
        'Search refs', 'Internal refs', 'Direct refs',
        'Social refs', 'Other refs', 'Fb refs', 'Tw refs'
    ]
    # ---- FIX DATAFRAME --------
    # fix any columns that may have float data types but should be integers
    for item in key_metrics + device_cols + referral_cols:
        df[item] = df[item].apply(lambda x: int(x))
    # fix any empty columns that should have strings but are 0
    for item in ['URL', 'Title', 'Publish date', 'Authors', 'Section', 'Tags']:
        df[item] = df[item].apply(lambda x: x if x != 0 else 'none')
    # ---- MODIFY DATAFRAME --------
    # add asset ids if relevant to page
    df['asset id'] = df['URL'].apply(
        lambda x: (re.search(
            r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    df['Date'] = pd.to_datetime(df['Publish date'])
    df['DayOfWeek'] = df['Date'].dt.day_name()
    # sort by pub date for following aggregate functions
    # print(df_articles_temp[df_articles_temp['Publish date'] == 0])
    df = df.sort_values(
        by=['Publish date'], ascending=False)
    # aggregate article data by asset ID
    aggregation_functions = {
        'URL': 'last',
        'Title': 'last',
        'Publish date': 'last',
        'Authors': 'last',
        'Section': 'last',
        'Tags': 'last',
        'Visitors': 'sum',
        'Returning vis.': 'sum',
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
    df_articles = df.groupby(
        df['asset id']).aggregate(aggregation_functions)
    # ADD MORE COLUMNS NEEDED FOR ARTICLES
    df_articles['Category'] = df_articles['Section'].apply(
        lambda x: x.split('|')[0] if x != 0 else 'none'
    )
    df_articles['Subcategory'] = df_articles['Section'].apply(
        lambda x: x.split('|')[-1] if x != 0 else 'none'
    )
    # convert tags category to string if not already
    df_articles['Tags'] = df_articles['Tags'].apply(
        lambda x: x if x != 0 else 'none'
    )
    df_articles.to_csv('authors-test.csv')
    data = {}
    data['name'] = name
    data['pv'] = df_articles['Views'].sum()
    data['vis'] = df_articles['Visitors'].sum()
    data['search %'] = int(round(100 * (df_articles['Search refs'].sum() / df_articles['Views'].sum()), 0))
    data['social %'] = int(round(100 * (df_articles['Social refs'].sum() / df_articles['Views'].sum()), 0))
    # data['vis_returning%'] = round(100 * (df_articles['Returning vis.'].sum() / df_articles['Views'].sum()), 1)
    time = df_articles['Engaged minutes'].sum() / df_articles['Visitors'].sum()
    mins = int(time)
    data['minutes'] = df_articles['Engaged minutes'].sum()
    seconds = int(round((time - mins) * 60, 0))
    data['avg. time'] = f'''{mins}:{seconds:02d}'''
    data['posts'] = df_articles['asset id'].count()
    data['views mean'] = int(round(df_articles['Views'].mean(), 0))
    data['views median'] = int(round(df_articles['Views'].median(), 0))
    data['posts_id'] = df_articles['asset id'].unique()
    if site_name == 'spectator':
        data['clicks'] = clicks_parse('spectator-last-clicks.csv', data['posts_id'])
    elif site_name == 'record':
        data['clicks'] = clicks_parse('record-last-clicks.csv', data['posts_id'])
    elif site_name == 'examiner':
        data['clicks'] = clicks_parse('examiner-last-clicks.csv', data['posts_id'])
    return data


def output(data):
    d = data
    s = ''
    s += f'''{d['name']},'''
    s += f'''{d['posts']},'''
    s += f'''{d['views median']},{d['avg. time']},'''
    if 'clicks' in data:
        s += f'''{d['clicks']['last click']},'''
        s += f'''{d['clicks']['last 3 clicks']},'''
        s += f'''{round(1000 * (d['clicks']['last click'] / d['vis']), 2)},'''
        s += f'''{round(1000 * (d['clicks']['last 3 clicks'] / d['vis']), 2)},''' 
    else:
        s += f''',,,,'''
    s += f'''{d['social %']},{d['search %']},'''
    s += f'''{d['pv']},'''
    s += f'''{d['minutes']}'''
    # s += f'''{d['posts_id']}'''
    return s


def clicks_parse(fn, ids):
    df = read_csv(
        filename=fn,
        folders=['data', 'authors'],
        cols_to_keep=clicks_cols,
        tabs=True,
    )

    for item in ["Last 3 Clicks", "Last Clicks"]:
        df[item] = df[item].apply(lambda x: int(x))
    df['asset id'] = df['Post Page Url'].apply(
        lambda x: (re.search(
            r'.*(\d{7})-.*', x)).group(1) if re.search(r'.*(\d{7})-.*', x) else 'none'
    )
    # aggregate article data by asset ID
    aggregation_functions = {
        'Post Page Url': 'last',
        'Title': 'last',
        'Last 3 Clicks': 'sum',
        'Last Clicks': 'sum',
        'asset id': 'first',
    }
    df_clicks = df.groupby(
        df['asset id']).aggregate(aggregation_functions)
    df_clicks.to_csv('clicks-test.csv')
    data = {'last click': 0, 'last 3 clicks': 0}
    for id in ids:
        if id in df_clicks['asset id'].values:
            data['last click'] += df_clicks[df_clicks['asset id'] == id]['Last Clicks'].sum()
            data['last 3 clicks'] += df_clicks[df_clicks['asset id'] == id]['Last 3 Clicks'].sum()
        # get last clicks from all items
    return data


# --[ MAIN ]---------
for key, value in params['sites'].items():
    site_name = value['name']
    print('Author, Posts, Views Median, Avg. Time, Last Clicks, Last 3 Clicks, Last Click / 1000 visitors, Last 3 Clicks / 1000 visitors, Social %, Search %, Views, Minutes')
    for author in value['authors']:
        author_name = author.lower().replace(' ', '').replace('\'', '')
        file_name = f'{site_name}-{author_name}.csv'
        data = authors_parse(file_name, author, site_name)
        print(output(data))
