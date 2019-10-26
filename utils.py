# standard
import random
import pathlib
import sys
import re
# external
import htmlmin
import requests
import boto3

# [ FILE I/O ]-------------------------


def read_file(filename, folders=None):
    # folders = list of subdirectory names
    #           in tree from cwd
    # print(f'''Retrieving {filename} in {folder}''')
    if folders:
        if not isinstance(folders, list):
            print("Folders parameter MUST be a list!")
            sys.exit()
        p = pathlib.Path.cwd().joinpath(*folders)
    else:
        p = pathlib.Path.cwd()
    path = p.joinpath(filename)
    return path.read_text()


def put_file(data, filename, folders=None):
    # WARNING: THIS OVERWRITES DATA
    # print(f'''Writing {filename} in {folder}''')
    if folders:
        if not isinstance(folders, list):
            print("Folders paramaeter MUST be a list!")
            sys.exit()
        p = pathlib.Path.cwd().joinpath(*folders)
    else:
        p = pathlib.Path.cwd()
    path = p.joinpath(filename)
    path.write_text(data)
    return


# [ WEB I/O ]--------------------------


def get_web_data(s_url, return_json=True):
    print("+++++++++++++\nNow in fetch_data module ...")
    # string s_url
    # boolean b_json whether to return json or text
    # list of strings that are really keys to drill down the dict
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A41DS1497c Safari/602.1',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/74.0.3729.131 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.0; SM-G570M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
    ]
    headers = {'user-agent': random.choice(user_agents)}
    # print(f"Fetch headers: {headers}")
    r = requests.get(s_url, headers=headers)
    if return_json is False:
        return r.text()
    else:
        return r.json()


def put_S3(file_name):
    # should have variable for cach controle
    # should have variable for file path
    print("++++++++++++\nNow in Put S3 module ...")
    s3 = boto3.resource('s3')
    js_file_name = f"{file_name}.js"
    data = open(f'./build/{js_file_name}', 'rb')
    s3.Bucket('picabot').put_object(Key=f'pagejs/{js_file_name}', Body=data, CacheControl="max-age=1800")
    return


def minify_css(s):
    print("++++++++++\nNow in fetch_css module ...")
    # s is string of content from some .css file
    response = requests.post('https://cssminifier.com/raw', data={'input': s})
    css = response.text
    return css

# [ TEXT CRUNCHING ]-------------------


def minify_html(s):
    # returns string of minified html
    return htmlmin.minify(s, remove_comments=True, remove_empty_space=True)

# [ NUMBER CRUNCHING ]-----------------
# best practice to always return numbers, not text


def percentage(part, total):
    # have to take into account part might be none (actually '')
    if part != '':
        result = round((float(part) / float(total)) * 100, 0)
        return result
    else:
        return 0


# exception, it has to return a string
def humanize(value, fraction_point=1):
    if value != '':
        if value == 0:
            return '0'
        powers = [10 ** x for x in (12, 9, 6, 3, 0)]
        human_powers = ('T', 'B', 'M', 'K', '')
        is_negative = False
        if not isinstance(value, float):
            value = float(value)
        if value < 0:
            is_negative = True
            value = abs(value)
        for i, p in enumerate(powers):
            if value >= p:
                return_value = str(round(value / (p / (10.0 ** fraction_point)))
                                   / (10 ** fraction_point)) + human_powers[i]
                break
        if is_negative:
            return_value = "-" + return_value
        # remove pesky situation where xXX.0 occurs
        # return_value = return_value.replace('.0', '')
        # print("Return value is: ", return_value)
        return_value = re.sub(r'.0$', '', return_value)
        return return_value.replace('.0K', 'K')
    else:
        return '0'
