var = {
    # FILES TO PROCESS
    'spectator': {
        'daily': {
            'period': 90,
            'term': 'days',
            'url': 'https://www.thespec.com',
            'files': {
                'site_csv': 'spectator-site-2019.csv',
                'pages_csv': 'spectator-pages.csv',
            }
        },
        'weekly': {
            'period': 13,
            'term': 'weeks',
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
            'term': 'months',
            'url': 'https://www.thespec.com',
            'files': {
                'site_csv': 'spectator-site-2019.csv',
                'pages_csv': 'spectator-pages.csv',
                'referrers': 'spectator-referrers.csv',
                'long_reads_csv': 'spectator-pages.csv',
                'top_sections': 'spectator-sections.csv',
            }
        }
    },
    'record': {
        'daily': {
            'period': 90,
            'term': 'days',
            'url': 'https://www.therecord.com',
        },
        'weekly': {
            'period': 90,
            'term': 'weeks',
            'url': 'https://www.therecord.com',
            'files': {
                'site_csv': 'record-site-2019.csv',
                'pages_csv': 'record-pages-last-week.csv',
                'referrers': 'record-referrers-last-week.csv',
            }
        },
        'monthly': {
            'period': 3,
            'term': 'months',
            'url': 'https://www.therecord.com',
            'files': {
                'site_csv': 'record-site-2019.csv',
                'pages_csv': 'record-pages.csv',
                'referrers': 'record-referrers.csv',
                'long_reads_csv': 'record-pages.csv',
                'top_sections': 'record-sections.csv',
            }
        }
    },
    'examiner': {
        'monthly': {
            'period': 3,
            'term': 'months',
            'url': 'https://www.peterboroughexaminer.com',
            'files': {
                'site_csv': 'examiner-site-2019.csv',
                'pages_csv': 'examiner-pages.csv',
                'referrers': 'examiner-referrers.csv',
                'long_reads_csv': 'examiner-pages.csv',
                'top_sections': 'examiner-sections.csv',
            }
        }
    },
    'standard': {
        'monthly': {
            'period': 3,
            'term': 'months',
            'url': 'https://www.stcatharinesstandard.ca',
            'files': {
                'site_csv': 'standard-site-2019.csv',
                'pages_csv': 'standard-pages.csv',
                'referrers': 'standard-referrers.csv',
                'long_reads_csv': 'standard-pages.csv',
                'top_sections': 'standard-sections.csv',
            }
        }
    },
    'tribune': {
        'monthly': {
            'period': 3,
            'term': 'months',
            'url': 'https://www.wellandtribune.ca',
            'files': {
                'site_csv': 'tribune-site-2019.csv',
                'pages_csv': 'tribune-pages.csv',
                'referrers': 'tribune-referrers.csv',
                'long_reads_csv': 'tribune-pages.csv',
                'top_sections': 'tribune-sections.csv',
            }
        }
    },
    'review': {
        'monthly': {
            'period': 3,
            'term': 'months',
            'url': 'https://www.niagarafallsreview.ca',
            'files': {
                'site_csv': 'review-site-2019.csv',
                'pages_csv': 'review-pages.csv',
                'referrers': 'review-referrers.csv',
                'long_reads_csv': 'review-pages.csv',
                'top_sections': 'review-sections.csv',
            }
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
    # REFERRERS STATS
    'referrers_cols_keep': [
        'Referrer Type',
        'Domain',
        'Referred Views',
    ],
    # SECTIONS STATS
    'sections_cols_keep': [
        "Section", "Posts", "Visitors", "Views", "Engaged minutes", 
        "Returning vis.", "Avg. views ret. vis.", "Avg. minutes ret. vis.", 
        "Search refs", "Internal refs", "Other refs", 
        "Direct refs", "Social refs", "Fb refs", "Social interactions"
    ],
    # handy helpers
    'newline': '\n',
    'dbline': '\n\n',
}
