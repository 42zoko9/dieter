import datetime
import json
import re
import urllib.parse
import urllib.request
from typing import List

import pandas as pd


class Twitter:
    def __init__(self, user_id: str, bearer_token: str):
        self.user_id = user_id
        self.bearer_token = bearer_token

    def search_ringfitadventure_results(self, start_date: str) -> List[str]:
        '''リングフィット実績画像のurlをリストで返す

        Args:
            start_date (str): 検索する時に遡る日付, YYYY-mm-dd, 最大７日まで遡ることが可能

        Returns:
            List[str]: リングフィットの実績画像のurlをまとめたリスト
        '''
        # dateのフォーマット確認
        if not re.search(r'^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]$', start_date):
            raise ValueError('"start_date" must be yyyy-mm-dd.')

        # 日付が現時点よりも７日以上前でないことを確認
        now = pd.to_datetime(start_date).tz_localize('Asia/Tokyo')
        if now < (pd.Timestamp.today(tz='Asia/Tokyo') - datetime.timedelta(days=7)):
            raise ValueError('this method can search tweets from the last seven days')

        # #RingFitAdventureのタグがついたツイートを検索する
        headers = {
            'Authorization': 'Bearer ' + self.bearer_token
        }
        query = 'from:{} #RingFitAdventure'.format(self.user_id)
        params = {
            'query': query,
            'expansions': 'attachments.media_keys',
            'media.fields': 'url',
            'start_time': now.tz_convert('UTC').strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        p = urllib.parse.urlencode(params, safe='', quote_via=urllib.parse.quote)
        url = 'https://api.twitter.com/2/tweets/search/recent?' + p
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            body = res.read()

        # リングフィットの実績画像のurlをリストにまとめて出力
        tweets = json.loads(body.decode('utf-8'))
        try:
            medias = tweets['includes']['media']
            return [m['url'] for m in medias]
        except KeyError:
            print('tweets dont be have medias.')
            return []


if __name__ == '__main__':
    import configparser

    date = '2021-11-24'
    ini_path = 'local.ini'
    config_ini = configparser.ConfigParser()
    config_ini.read(ini_path)
    user_id = config_ini.get('TWITTER', 'user-id')
    token = config_ini.get('TWITTER', 'escaped-bearer-token')
    tw = Twitter(user_id, token)
    print(tw.search_ringfitadventure_results(date))
