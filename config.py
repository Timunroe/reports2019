var = {
    # FILES TO PROCESS
    'spectator': {
        'daily': {
            'period': 90,
            'url': 'https://www.thespec.com',
            'files': {
                'site_csv': 'spectator-site-yesterday.csv',
                'site_archives_csv': 'spectator-site-2019.csv',
                'pages_csv': 'spectator-pages-yesterday.csv',

            }
        },
        'weekly': {
            'period': 13,
            'url': 'https://www.thespec.com',
            'files': {
                'site_csv': 'spectator-site-2019.csv',
                'pages_csv': 'spectator-pages-last-week.csv',
                'referrers': 'spectator-referrers-last-week.csv',
                'long_reads': 'spectator-pages-last-week.csv',
                'top_sections': 'spectator-top-sections-last-week.csv',
                'top_pages': 'spectator-top-pages-last-week.csv',
            }
        },
        'monthly': {
            'period': 3,
            'url': 'https://www.thespec.com',
            'files': {
                'site_csv': 'spectator-site-2019.csv',
                'pages_csv': 'spectator-pages.csv',
                'referrers': 'spectator-referrers.csv',
                'long_reads_csv': 'spectator-pages.csv',
                'top_sections': 'spectator-top-sections.csv',
                'top_pages': 'spectator-top-pages.csv',
            }
        }
    },
    'record': {
        'daily': {
            'period': 90,
            'url': 'https://www.therecord.com',
        },
        'weekly': {
            'period': 90,
            'url': 'https://www.therecord.com',
            'files': {
                'site_csv': 'record-site-2019.csv',
                'pages_csv': 'record-pages-last-week.csv',
                'referrers': 'record-referrers-last-week.csv',
            }
        },
        'monthly': {
            'period': 3,
            'url': 'https://www.therecord.com',
            'files': {
                'site_csv': 'record-site-2019.csv',
                'pages_csv': 'record-pages.csv',
                'referrers': 'record-referrers.csv',
                'long_reads_csv': 'record-pages.csv',
                'top_sections': 'record-top-sections.csv',
                'top_pages': 'record-top-pages.csv',
            }
        }
    },
    'examiner': {

    },
    'standard': {

    },
    'tribune': {

    },
    'review': {

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
    # REFERRERS STATS
    'referrers_cols_keep': [
        'Referrer Type',
        'Domain',
        'Referred Views',
    ],
    
    # handy helpers
    'newline': '\n',
    'dbline': '\n\n',
}
