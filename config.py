var = {
    # FILES TO PROCESS
    'daily': {
        'period': 90,
        'spectator': {
            'site_csv': 'spectator-site-yesterday-thespec-com-any.csv',
            'site_archives_csv': 'spectator-site-2019.csv',
            'pages_csv': 'spectator-pages-yesterday-thespec-com-any.csv',
        }
    },
    'weekly': {
        'period': 13,
        'spectator': {
            'site_csv': 'spectator-site-last-week-thespec-com-any.csv',
            'site_archives_csv': 'spectator-site-2019.csv',
            'pages_csv': 'spectator-pages-last-week-thespec-com-any.csv',
            'referrers': 'spectator-referrers-last-week-thespec-com-any.csv',
            'long_reads': '',
            'top_sections': '',
            'top_pages': '',
        },
        'record': {
            'site_csv': 'record-site-last-week-therecord-com-any.csv',
            'site_archives_csv': 'record-site-2019.csv',
            'pages_csv': 'record-pages-last-week-thespec-com-any.csv',
            'referrers': 'record-referrers-last-week-thespec-com-any.csv',
        }
    },
    # SITE STATS
    'site_cols_keep': [
        'Date',
        'Posts',
        'New Posts',
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
    ],
    # ARTICLES STATS
    'pages_cols_keep': [
        'URL',
        'Title',
        'Publish date',
        'Authors',
        'Section',
        'Tags',
        'Visitors',
        'Views',
        'Engaged minutes',
        'New vis.',
        'Returning vis.',
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
        'Social interactions',
        'Fb interactions',
        'Tw interactions',
    ],
    # handy helpers
    'newline': '\n',
    'dbline': '\n\n',
}
