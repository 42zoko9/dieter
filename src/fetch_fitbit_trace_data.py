import os
import sys
import traceback
import configparser
import urllib.request
from fetch_fitbit_authorization_code import fetch_authorization_code
from fetch_fitbit_tokens import fetch_tokens, refresh_access_token

def export_trace_data(category:str, date:str) -> None:
    '''fitbitからトレースデータを取得しjsonファイルに保存

    Args:
        category (str): activities, food, sleep
        date (str): 取得したいデータの日付, yyyy-mm-dd
    '''
    # categoryの前処理
    if category == 'activities':
        uri_category = category
    elif category == 'food':
        uri_category = 'foods/log'
    elif category == 'sleep':
        uri_category = category

    # access_tokenとrefresh_tokenの取得
    config_ini = configparser.ConfigParser()
    path_config_ini = 'fitbit_config.ini'
    redirect_uri = 'http://localhost:8080'
    if os.path.isfile(path_config_ini):
        pass
    else:
        scope = ['activity', 'heartrate', 'nutrition', 'sleep']
        expiers_in = 604800
        fetch_authorization_code(redirect_uri, scope, expiers_in)
        fetch_tokens(redirect_uri)
    config_ini.read(path_config_ini, encoding='utf-8')
    try:
        access_token = config_ini.get('FITBIT', 'access_token')
    except:
        print('the access token is not listed in fitbit_config.ini')
        try:
            fetch_tokens(redirect_uri)
        except:
            print(traceback.format_exc())
            print('Notice: the authorization code may have expired.')
            sys.exit()
    refresh_token = config_ini.get('FITBIT', 'refresh_token')

    # 該当データを取得
    # 未着用でもデータは出力される   
    try:
        headers = {'Authorization': 'Bearer ' + access_token}
        url = 'https://api.fitbit.com/1.2/user/-/{category}/date/{date}.json'.format(
            category=uri_category, date=date
        )
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            result = res.read()
    except urllib.error.HTTPError:
        refresh_access_token()
        print('refresh acccess token')
        config_ini.read(path_config_ini, encoding='utf-8')
        access_token = config_ini.get('FITBIT', 'access_token')
        headers = {'Authorization': 'Bearer ' + access_token}
        url = 'https://api.fitbit.com/1.2/user/-/{category}/date/{date}.json'.format(
            category=uri_category, date=date
        )
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            result = res.read()
    # jsonファイルとして保存
    path_jsonfile = 'data/fitbit/{category}/{date}.json'.format(
        category=category, date=date
    )
    with open(path_jsonfile, 'w') as jsonfile:
        jsonfile.write(result.decode('utf-8'))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('date', type=str)
    args = parser.parse_args()

    export_trace_data('activities', args.date)
    export_trace_data('food', args.date)
    export_trace_data('sleep', args.date)
