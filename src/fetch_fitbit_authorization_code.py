from typing import List
import os
import sys
import urllib.parse, urllib.request
import configparser
import webbrowser

def fetch_authorization_code(
    redirect_uri:str,
    scope: List[str],
    expiers_in: int = 604800
) -> None:
    '''fitbit APIの認可コードを取得しiniファイルに上書きする

    Args:
        redirect_uri (str): リダイレクト先のURI
        scope (List): APIを受け付ける領域の一覧
        expiers_in (int): 認可コードの寿命
    '''
    # fitbit_config.iniが存在しない場合，ファイルを作成する
    config_ini = configparser.ConfigParser()
    if os.path.isfile('fitbit_config.ini'):
        config_ini.read('fitbit_config.ini', encoding='utf-8')
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
    with open('fitbit_config.ini', 'w') as configfile:
        config_ini.write(configfile)

if __name__ == '__main__':
    # パラメータの設定
    redirect_uri = 'http://localhost:8080'
    scope = ['activity', 'heartrate', 'nutrition', 'sleep']
    expiers_in = 604800

    # 認可コードの取得
    fetch_authorization_code(redirect_uri, scope, expiers_in)





