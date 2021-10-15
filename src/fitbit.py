from typing import List
import os
import sys
import ast
import base64
import configparser
import webbrowser
import urllib.parse, urllib.request

def export_trace_data(
    category: str,
    date: str,
    redirect_uri: str = 'http://localhost:8080',
    path_config_ini: str = 'config.ini'
) -> None:
    '''fitbitからトレースデータを取得しjsonファイルに出力

    Args:
        category (str): "activities", "food", "sleep"のいずれかを入力
        date (str): 取得したいデータの日付, "yyyy-mm-dd"形式で入力
        redirect_uri (str): リダイレクト先のURI
        path_config_ini (str): config.iniファイルのパス
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
    if os.path.isfile(path_config_ini):
        pass
    else:
        scope = ['activity', 'heartrate', 'nutrition', 'sleep']
        expiers_in = 604800
        write_authorization_code(redirect_uri, scope, expiers_in)
        write_tokens(redirect_uri)
    config_ini.read(path_config_ini, encoding='utf-8')
    try:
        access_token = config_ini.get('FITBIT', 'access_token')
    except Exception as e:
        print(e)
        print('the access token is not listed in fitbit_config.ini')

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

def write_tokens(
    redirect_uri: str = 'http://localhost:8080',
    path_config_ini: str = 'config.ini'
) -> None:
    '''fitbitのaccess_tokenとrefresh_tokenを取得しfitbit_config.iniに書き出す

    Args:
        redirect_uri (str): リダイレクト先のURI
        path_config_ini (str): config.iniファイルのパス
    '''
    # fitbit_config.iniの所在確認
    config_ini = configparser.ConfigParser()
    if os.path.isfile(path_config_ini):
        pass
    else:
        raise ValueError('"{}" is not found. try "write_authorization_code"'.format(path_config_ini))
    config_ini.read(path_config_ini, encoding='utf-8')
    client_id = config_ini.get('FITBIT', 'client_id')
    client_secret = config_ini.get('FITBIT', 'client_secret')
    auth_code = config_ini.get('FITBIT', 'authorization_code')

    # access_tokenとrefresh_tokenの取得
    basic_user_and_pasword = base64.b64encode('{}:{}'.format(client_id, client_secret).encode('utf-8'))
    url = 'https://api.fitbit.com/oauth2/token'
    data = {
        'clientId': client_id,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': auth_code
    }
    headers = {
        'Authorization': 'Basic ' + basic_user_and_pasword.decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=headers)
    except Exception as e:
        print(e)
        print('Notice: the authorization code may have expired.')
    
    with urllib.request.urlopen(req) as res:
        body = res.read()
    res_dict = ast.literal_eval(body.decode('utf-8'))

    # fitbit_config.iniへ書き込み
    config_ini["FITBIT"]['access_token'] = res_dict['access_token']
    config_ini["FITBIT"]['refresh_token'] = res_dict['refresh_token']
    with open(path_config_ini, 'w') as configfile:
        config_ini.write(configfile)

def refresh_access_token(
    redirect_uri: str = 'http://localhost:8080',
    path_config_ini: str = 'config.ini'
) -> None:
    '''access_tokenを再取得しiniファイルを更新する

    Args:
        redirect_uri (str): リダイレクト先のURI
        path_config_ini (str): config.iniファイルのパス
    '''
    config_ini = configparser.ConfigParser()
    config_ini.read(path_config_ini, encoding='utf-8')
    client_id = config_ini.get('FITBIT', 'client_id')
    client_secret = config_ini.get('FITBIT', 'client_secret')
    refresh_token = config_ini.get('FITBIT', 'refresh_token')
    basic_user_and_pasword = base64.b64encode('{}:{}'.format(client_id, client_secret).encode('utf-8'))
    url = 'https://api.fitbit.com/oauth2/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Authorization': 'Basic ' + basic_user_and_pasword.decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=headers)
    except Exception as e:
        print(e)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
    except Exception as e:
        print(e)
        print('try "write_tokens"')
    res_dict = ast.literal_eval(body.decode('utf-8'))

    # fitbit_config.iniへ書き込み
    config_ini["FITBIT"]['access_token'] = res_dict['access_token']
    with open(path_config_ini, 'w') as configfile:
        config_ini.write(configfile)

def write_authorization_code(
    scope: List[str],
    expiers_in: int = 604800,
    redirect_uri: str = 'http://localhost:8080',
    path_config_ini: str = 'config.ini'
) -> None:
    '''fitbit APIの認可コードを取得しiniファイルに書き出す

    Args:
        scope (List): APIを受け付ける領域の一覧
        expiers_in (int): 認可コードの寿命
        redirect_uri (str): リダイレクト先のURI
        path_config_ini (str): config.iniファイルのパス
    '''
    # fitbit_config.iniが存在しない場合，ファイルを作成する
    config_ini = configparser.ConfigParser()
    if os.path.isfile(path_config_ini):
        config_ini.read(path_config_ini, encoding='utf-8')
        client_id = config_ini['FITBIT']['client_id']
    else:
        config_ini['FITBIT'] = {}
        client_id = input('Enter client id of fitbit: ')
        config_ini['FITBIT']['client_id'] = client_id
        client_secret = input('Enter client secret of fitbit: ')
        config_ini['FITBIT']['client_secret'] = client_secret
    
    # authorization codeが既に記入されているか確認
    try: 
        auth_code = config_ini.get('FITBIT', 'authorization_code')
        is_execution = input('It looks like you already have authorization code. Do you want to run it? [y/N]').lower()
        if is_execution in ['y', 'yes']:
            pass
        elif is_execution in ['n', 'no']:
            sys.exit()
        else:
            raise ValueError('input value is "y" or "N"')
    except configparser.NoOptionError:
        pass

    # authorization_codeの取得
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scope),
        'expires_in': expiers_in
    }
    p = urllib.parse.urlencode(params, safe='', quote_via=urllib.parse.quote)
    url = 'https://www.fitbit.com/oauth2/authorize?' + p
    webbrowser.open(url)
    auth_code = input('Enter authorization code (Excluding "#_=_"): ')
    config_ini['FITBIT']['authorization_code'] = auth_code

    # iniファイルに書き込み
    with open(path_config_ini, 'w') as configfile:
        config_ini.write(configfile)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='run "write_*()')
    parser.add_argument('--date', type=str, default='2021-10-01')
    args = parser.parse_args()

    if args.write:
        scope = ['activity', 'heartrate', 'nutrition', 'sleep']
        write_authorization_code(scope)
        write_tokens()
    else:
        export_trace_data('activities', args.date)
        export_trace_data('food', args.date)
        export_trace_data('sleep', args.date)
