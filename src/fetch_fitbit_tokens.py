import os
import sys
import traceback
import configparser
import urllib.parse, urllib.request
import base64
import ast
from fetch_fitbit_authorization_code import fetch_authorization_code

def fetch_tokens(
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
        scope = ['activity', 'heartrate', 'nutrition', 'sleep']
        expiers_in = 604800
        fetch_authorization_code(redirect_uri, scope, expiers_in)
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
    except:
        print(traceback.format_exc())
        print('Notice: the authorization code may have expired.')
        sys.exit()
    with urllib.request.urlopen(req) as res:
        body = res.read()
    res_dict = ast.literal_eval(body.decode('utf-8'))

    # fitbit_config.iniへ書き込み
    config_ini["FITBIT"]['access_token'] = res_dict['access_token']
    config_ini["FITBIT"]['refresh_token'] = res_dict['refresh_token']
    with open(path_config_ini, 'w') as configfile:
        config_ini.write(configfile)

def refresh_access_token(
    path_config_ini: str = 'config.ini'
) -> None:
    '''access_tokenを再取得しiniファイルを更新する

    Args:
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
    except:
        print(traceback.format_exc())
        sys.exit()
    with urllib.request.urlopen(req) as res:
        body = res.read()
    res_dict = ast.literal_eval(body.decode('utf-8'))

    # fitbit_config.iniへ書き込み
    config_ini["FITBIT"]['access_token'] = res_dict['access_token']
    with open(path_config_ini, 'w') as configfile:
        config_ini.write(configfile)

if __name__ == '__main__':
    fetch_tokens()
