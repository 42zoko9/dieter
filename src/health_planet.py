import datetime
import json
import re
import urllib.parse
import urllib.request
from typing import Any, Dict

import pandas as pd


class HealthPlanet:

    def __init__(self, access_token: str):
        self.access_token = access_token

    def fetch_body_composition_data(self, from_date: str, to_date: str) -> Dict[str, Any]:
        '''体重と体脂肪率を取得し辞書型で取得する

        Args:
            from_date (str): データを取得したい期間の開始日、"yyyy-mm-dd"形式で入力
            to_date (str): データを取得したい期間の終了日、"yyyy-mm-dd"形式で入力

        Returns:
            Dict[str, Any]: 体組成データ
        '''
        # from_dateのフォーマット確認
        if not re.search(r'^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]$', from_date):
            raise ValueError('"from_date" must be yyyy-mm-dd.')

        # to_dateのフォーマット確認
        if not re.search(r'^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]$', to_date):
            raise ValueError('"to_date" must be yyyy-mm-dd.')

        # 日付の前処理
        from_dt = from_date.replace('-', '') + '000000'
        to_dt = to_date.replace('-', '') + '235959'
        from_datetime = pd.to_datetime(from_dt).tz_localize('Asia/Tokyo')
        to_datetime = pd.to_datetime(to_dt).tz_localize('Asia/Tokyo')
        if from_datetime > to_datetime:
            raise ValueError('"to_date" is greater than "from_date".')
        # NOTE: error: No overload variant of "__sub__" of "Timestamp" matches argument type "DateOffset"
        # limit_datetime = pd.Timestamp.today(tz='Asia/Tokyo') - DateOffset(months=3)
        limit_datetime = pd.Timestamp.today(tz='Asia/Tokyo') - datetime.timedelta(days=90)
        if from_datetime < limit_datetime:
            raise ValueError('"from_date" is over 3 month ago.')

        # 該当データを取得
        params = {
            'access_token': self.access_token,
            'data': '1',
            'from': from_dt,
            'to': to_dt,
            'tag': '6021,6022'
        }
        p = urllib.parse.urlencode(params)
        url = 'https://www.healthplanet.jp/status/innerscan.json/?' + p
        with urllib.request.urlopen(url) as res:
            result = res.read()
        return json.loads(result)


if __name__ == '__main__':
    # 以下，ローカル環境で動作検証時に使用
    import configparser
    import pprint

    ini_path = 'local.ini'
    config_ini = configparser.ConfigParser()
    config_ini.read(ini_path, encoding='utf-8')
    access_token = config_ini.get('HEALTH PLANET', 'access-token')

    d = '2021-11-01'
    hp = HealthPlanet(access_token)
    result = hp.fetch_body_composition_data(d, d)
    pprint.pprint(result)
