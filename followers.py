from requests_html import HTMLSession
import requests
import random
import re
import json
from datetime import date
import utils as u
import time
import secret
import tweepy

sites = [
    {
        'site': 'TS',
        'fb': 'https://www.facebook.com/torontostar/',
        'tw': 'TorontoStar',
        'yt': 'https://www.youtube.com/TorontoStar',
        'ig': 'https://www.instagram.com/thetorontostar/?hl=en',
        'pi': 'https://www.pinterest.ca/torontostar/',
        # 'li': '',
    },
    {
        'site': 'HS',
        'fb': 'https://www.facebook.com/hamiltonspectator/',
        'tw': 'TheSpec',
        'yt': 'https://www.youtube.com/thespecvideo',
        'ig': 'https://www.instagram.com/hamiltonspectator/?hl=en',
        'pi': 'https://www.pinterest.ca/thespectator/',
        # 'li': 'https://ca.linkedin.com/company/the-hamilton-spectator',
    },
    {
        'site': 'WRR',
        'fb': 'https://www.facebook.com/waterlooregionrecord/',
        'tw': 'WR_Record',
        'yt': 'https://www.youtube.com/phototherecord',
        'ig': 'https://www.instagram.com/waterlooregionrecord/?hl=en',
        'pi': 'https://www.pinterest.ca/WRrecord/',
        # 'li': ''
    },
    {
        'site': 'SCS',
        'fb': 'https://www.facebook.com/stcatharinesstandard/',
        'tw': 'StCatStandard',
        'yt': 'https://www.youtube.com/channel/UCcAzUYgemMC1igVHQwyw4uA',
        'ig': 'https://www.instagram.com/stcatharinesstandard/',
        'pi': '',
        # 'li': ''
    },
    {
        'site': 'NFR',
        'fb': 'https://www.facebook.com/niagarafallsreview/',
        'tw': 'NiaFallsReview',
        'yt': '',
        'ig': '',
        'pi': '',
        # 'li': ''
    },
    {
        'site': 'WT',
        'fb': 'https://www.facebook.com/wellandtribune/',
        'tw': 'WellandTribune',
        'yt': 'https://www.youtube.com/channel/UCVClY5BoeVYaj834JOKLZUw',
        'ig': 'https://www.instagram.com/thetribune/',
        'pi': '',
        # 'li': ''
    },
    {
        'site': 'PE',
        'fb': 'https://www.facebook.com/PeterboroughExaminer/',
        'tw': 'PtboExaminer',
        'yt': 'https://www.youtube.com/channel/UC9RwlcrujYFt_GRVayVt3_g',
        'ig': 'https://www.instagram.com/pboroexaminer/',
        'pi': '',
        # 'li': ''
    }
]


def li_followers(url):
    '''
body > main > div > div > div > div > section.top-card.module.card > div > div.top-card__details > div > div.top-card__information > span:nth-child(3)
    '''
    r = requests.get('https://www.linkedin.com/uas/login', auth=('tmunroe@thespec.com', 'WCr4EA6qmkkH'))
    print(r.status_code)
    print(r.text)
    return


def ig_followers(url):
    print('Starting IG section')
    '''
    follower count found in script json in head
    '''
    if url:
        session = HTMLSession()
        r = session.get(url)
        results = r.html.find('script')
        for result in results:
            if 'userInteractionCount' in result.text:
                d = json.loads(result.text)
                followers = d['mainEntityofPage']['interactionStatistic']['userInteractionCount']
                return followers.strip()
        results = r.html.find('meta')
        result = results[13].attrs['content']
        x = re.search(r"\d{1,3}(,\d{3})*(\.\d+)? Followers", result)
        if x:
            followers = x.group().replace(' Followers', '').replace(',', '')
            return followers.strip()
        else:
            return ''
    else:
        return 0


def yt_followers(url):
    print('Starting YouTube section')
    '''
    Data is added dynamically via script.
    Find script with desired phrase, regex out subscribers
    '''
    if url:
        session = HTMLSession()
        r = session.get(url)
        results = r.html.find('script')
        followers = '0'
        for result in results:
            if 'subscriber' in result.text:
                followers = (re.search(r'.*text\":\"(\d.*) subscribers.*', result.text)).group(1)
        return followers.strip()
    else:
        return '0'


def tw_followers(handle):
    print('Starting Twitter section')
    twitter_consumer_key = secret.KEYS['twitter']['consumer_key']
    twitter_consumer_secret = secret.KEYS['twitter']['consumer_secret']
    twitter_token_key = secret.KEYS['twitter']['access_token_key']
    twitter_token_secret = secret.KEYS['twitter']['access_token_secret']

    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_token_key, twitter_token_secret)

    api = tweepy.API(auth)
    user = api.get_user(handle)
    return user.followers_count


def fb_followers(url):
    '''
    #PagesProfileHomeSecondaryColumnPagelet > div > div:nth-child(1) > div > div._4-u2._6590._3xaf._4-u8 > div:nth-child(4) > div > div._4bl9 > div
    <div>21,582 people follow this</div>
    '''
    print('Starting Facebook section')
    session = HTMLSession()
    r = session.get(url)
    results = r.html.find('div._4bl9 > div')
    followers = '0'
    for result in results:
        if 'follow' in result.text:
            followers = result.text.replace('people follow this', '').replace(',', '')
    return followers.strip()


def pi_followers(url):
    print('Starting Pinterest section')
    if url:
        session = HTMLSession()
        r = session.get(url)
        r.html.render()
        results = r.html.find('span.tBJ.dyH.iFc.SMy._S5.pBj.DrD.mWe')
        followers = (results[0].text).replace(',', '')
        return followers.strip()
    else:
        return 0


def main():
    report = f'''SOCIAL MEDIA FOLLOWERS
Week No. {date.today().isocalendar()[1]}, {date.today().isocalendar()[0]}
==============================================
SITE      FB      TW    YT      IG    PI    LI
'''
    for site in sites:
        print(f'''Processing {site['site']}''')
        fb = fb_followers(site['fb'])
        print('fb followers: ', fb)
        time.sleep(random.randint(3, 7))
        tw = tw_followers(site['tw'])
        print('tw followers: ', tw)
        time.sleep(random.randint(3, 7))
        yt = yt_followers(site['yt'])
        print('yt followers: ', yt)
        time.sleep(random.randint(3, 7))
        ig = ig_followers(site['ig'])
        print('ig followers: ', ig)
        time.sleep(random.randint(3, 7))
        pi = pi_followers(site['pi'])
        print('pi followers: ', pi)
        # li = li_followers(site['li'])
        report += f'''\
----------------------------------------------
{site['site'].ljust(3)}  \
{str(fb).rjust(7)} \
{str(tw).rjust(7)} \
{str(yt).rjust(5)} \
{str(ig).rjust(7)} \
{str(pi).rjust(5)}
'''
    print(report)


main()
