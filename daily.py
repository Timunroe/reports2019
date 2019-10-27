from bottle import template
import pandas as pd
# standard
import json
import pprint
# mine
import utils as u
import config as c


'''
Read yesterday's file ...
Download yesterday's site stats, drop in daily folder
What safeguards to make sure it's the right file?
filename = spectator-site-yesterday-thespec-com-any.csv
> get date of stats, compare with last date in master file?

'''