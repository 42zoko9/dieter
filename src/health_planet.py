import os
from pandas.tseries.offsets import DateOffset
import urllib.request, urllib.parse
import pandas as pd
import json
import configparser
import argparse

def export_body_composition_data(from_date:str, to_date:str) -> None:
    '''Health Planetから体重と体脂肪率を取得しjson形式で保存する

    Args:
        from (str): データを取得したい期間の開始日、"yyyy-mm-dd"形式で入力
        to (str): データを取得したい期間の終了日、"yyyy-mm-dd"形式で入力
    '''
    # access tokenの読み込み
    config_ini = configparser.ConfigParser()
    if os.path.isfile('config.ini'):
        config_ini.read('config.ini', encoding='utf-8')
    else:
        raise Exception('config.ini is not found.')
    access_token = config_ini.get('HEALTH PLANET', 'access_token')

    # 日付の前処理
    from_dt = from_date.replace('-', '') + '000000'
    to_dt = to_date.replace('-', '') + '235959'
    from_datetime = pd.to_datetime(from_dt).tz_localize('Asia/Tokyo')
    limit_datetime = pd.Timestamp.today(tz='Asia/Tokyo') - DateOffset(months=3)
    if from_datetime < limit_datetime:
        raise Exception('from_date is over 3 month ago')
    
    # 該当データを取得
    # データが存在しない時はExceptionを返す
    params = {
        'access_token': access_token,
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
    if len(data) == 0:
        raise Exception('fetched data is empty')
    
    # jsonファイルを保存
    path_jsonfile = 'data/health_planet/{}.json'.format(from_date)
    with open(path_jsonfile, 'w') as jsonfile:
        jsonfile.write(result.decode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('from_date', type=str)
    parser.add_argument('to_date', type=str)
    args = parser.parse_args()

    result = export_body_composition_data(args.from_date, args.to_date)
    print(result)