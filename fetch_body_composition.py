from typing import List
from pandas.tseries.offsets import DateOffset
import urllib.request, urllib.parse
import pandas as pd
import json
import configparser
import argparse

def fetch_body_composition(token:str, from_date:str, to_date:str) -> List:
    '''Health Planetから体重と体脂肪率を取得する

    Args:
        token (str): アクセストークン
        from (str): データ取得開始日、yyyymmddで入力
        to (str): データ取得終了日、yyyymmddで入力

    Returns:
        List: 計測日と体重もしくは体脂肪率の辞書をまとめたリスト
    '''
    from_dt = from_date + '000000'
    to_dt = to_date + '235959'
    from_datetime = pd.to_datetime(from_dt).tz_localize('Asia/Tokyo')
    limit_datetime = pd.Timestamp.today(tz='Asia/Tokyo') - DateOffset(months=3)
    if from_datetime < limit_datetime:
        raise Exception('from_date is over 3 month ago')
    
    params = {
        'access_token': token,
        'data': '1',
        'from': from_dt,
        'to': to_dt,
        'tag': '6021,6022'
    }
    p = urllib.parse.urlencode(params)
    url = 'https://www.healthplanet.jp/status/innerscan.json/?' + p
    with urllib.request.urlopen(url) as res:
        html = res.read()
    res_dic = json.loads(html)
    data = res_dic['data']
    if len(data) == 0:
        raise Exception('fetched data is empty')
    return data

if __name__ == '__main__':
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')
    hp_access_token = config_ini.get('DEFAULT', 'hp_access_token')

    parser = argparse.ArgumentParser()
    parser.add_argument('from_date', type=str)
    parser.add_argument('to_date', type=str)
    parser.add_argument('-t', '--token', default=hp_access_token, type=str)
    args = parser.parse_args()

    result = fetch_body_composition(args.token, args.from_date, args.to_date)
    print(result)
