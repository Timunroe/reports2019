from bottle import template
import pandas as pd

# standard
# import json
import time
import pprint
import pathlib
import sys
import re
# import datetime
import math
# mine
import utils as u
import config as c


for item in c.dashboard['monthly']:
    html = template('dashboard-monthly.html', data=item)
    u.write_file(html, f'''{item['name']}_monthly.html''', folders=['build'])
    time.sleep(3)