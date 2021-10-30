import configparser
import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd
from pandas.tseries.offsets import DateOffset


@dataclass
class HealthPlanet:
    access_token: str = ''

    def read_config(self, path: str) -> None:
        '''HEALTH PLANET周りの環境変数が記述されたiniファイルを読み込み各インスタンス変数に代入する

        Args:
            path (str): 読み込むiniファイルのパス
        '''
        # 引数dateの型確認
        if type(path) != str:
            raise TypeError('"path" type must be str.')

        # pathの末尾が.iniでない場合は処理を停止
        if not re.search(r'^.+\.ini$', path):
            raise ValueError('"path" must be an .ini file.')

        # 出力先のディレクトリが存在しない場合は処理を停止
        if '/' in path:
            dirpath = '/'.join(path.split('/')[:-1])
            if not os.path.isdir(dirpath):
                raise ValueError('no such directory')

        # 実行
        config_ini = configparser.ConfigParser()
        config_ini.read(path, encoding='utf-8')
        self.access_token = config_ini.get('HEALTH PLANET', 'access_token')

    def fetch_body_composition_data(self, from_date: str, to_date: str) -> Dict[Any, Any]:
        '''体重と体脂肪率を取得し辞書型で取得する

        Args:
            from_date (str): データを取得したい期間の開始日、"yyyy-mm-dd"形式で入力
            to_date (str): データを取得したい期間の終了日、"yyyy-mm-dd"形式で入力

        Returns:
            Dict[Any, Any]: 体組成データ
        '''
        # 引数from_dateの型確認
        if type(from_date) != str:
            raise TypeError('"from_date" type must be str.')

        # from_dateのフォーマット確認
        if not re.search(r'^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]$', from_date):
            raise ValueError('"from_date" must be yyyy-mm-dd.')

        # 引数to_dateの型確認
        if type(to_date) != str:
            raise TypeError('"to_date" type must be str.')

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
        limit_datetime = pd.Timestamp.today(tz='Asia/Tokyo') - DateOffset(months=3)
        if from_datetime < limit_datetime:
            raise ValueError('"from_date" is over 3 month ago.')

        # 該当データを取得
        # データが存在しない時はExceptionを返す
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
        result_dic = json.loads(result)
        data = result_dic['data']
        # if len(data) == 0:
        #     raise Exception('fetched data is empty')
        return data
