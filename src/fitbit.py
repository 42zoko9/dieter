import configparser
from dataclasses import dataclass
from typing import List, Dict, Any
import os
import sys
import json
import base64
import configparser
import webbrowser
import urllib.request, urllib.parse

@dataclass
class Fitbit:
    client_id: str = ''
    client_secret: str  = ''
    auth_code: str = ''
    access_token: str = ''
    refresh_token: str = ''

    def read_config(self, path: str):
        config_ini = configparser.ConfigParser()
        config_ini.read(path, encoding='utf-8')
        self.client_id = config_ini.get('FITBIT', 'client_id')
        self.client_secret = config_ini.get('FITBIT', 'client_secret')
        self.auth_code = config_ini.get('FITBIT', 'authorization_code')
        self.access_token = config_ini.get('FITBIT', 'access_token')
        self.refresh_token = config_ini.get('FITBIT', 'refresh_token')

    def fetch_trace_data(
        self,
        category: str,
        date: str
    ) -> Dict[Any, Any]:
        '''fitbitからトレースデータを取得しjsonファイルに出力

        Args:
            category (str): "activities", "foods", "sleep"のいずれかを入力
            date (str): 取得したいデータの日付, "yyyy-mm-dd"形式で入力
        '''
        # categoryの前処理
        if category == 'activities':
            uri_category = category
        elif category == 'foods':
            uri_category = 'foods/log'
        elif category == 'sleep':
            uri_category = category

        # 該当データを取得
        # 未着用でもデータは出力される   
        try:
            headers = {'Authorization': 'Bearer ' + self.access_token}
            url = 'https://api.fitbit.com/1.2/user/-/{category}/date/{date}.json'.format(
                category=uri_category, date=date
            )
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError:
            self.refresh_access_token()
            print('refreshed acccess token')
            headers = {'Authorization': 'Bearer ' + self.access_token}
            url = 'https://api.fitbit.com/1.2/user/-/{category}/date/{date}.json'.format(
                category=uri_category, date=date
            )
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as res:
                body = res.read()
        
        # 辞書型で出力
        return json.loads(body.decode('utf-8'))

    def update_tokens(
        self,
        redirect_uri: str = 'http://localhost:8080',
    ):
        '''fitbitのaccess_tokenとrefresh_tokenを取得する

        Args:
            redirect_uri (str): リダイレクト先のURI
        '''
        # access_tokenとrefresh_tokenの取得
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(self.client_id, self.client_secret).encode('utf-8'))
        url = 'https://api.fitbit.com/oauth2/token'
        data = {
            'clientId': self.client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': self.auth_code
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
        res_dict = eval(body.decode('utf-8'))
        self.access_token = res_dict['access_token']
        self.refresh_token = res_dict['refresh_token']

    def refresh_access_token(self) -> None:
        '''refresh_token経由でaccess_tokenを再取得する
        '''
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(self.client_id, self.client_secret).encode('utf-8'))
        url = 'https://api.fitbit.com/oauth2/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
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
            print('try method "fetch_tokens"')
        res_dict = eval(body.decode('utf-8'))
        self.access_token = res_dict['access_token']

    def update_authorization_code(
        self,
        scope: List[str] = ['activity', 'heartrate', 'nutrition', 'sleep'],
        expiers_in: int = 604800,
        redirect_uri: str = 'http://localhost:8080',
    ):
        '''fitbit APIの認可コードを取得する

        Args:
            scope (List): APIを受け付ける領域の一覧
            expiers_in (int): 認可コードの寿命
            redirect_uri (str): リダイレクト先のURI
            path_config_ini (str): config.iniファイルのパス
        '''
        # client_idとclient_secretの更新
        if self.client_id == '':
            client_id = input('Enter client id of fitbit: ')
            self.client_id = client_id
        if self.client_secret == '':
            client_secret = input('Enter client secret of fitbit: ')
            self.client_secret = client_secret
        
        # authorization codeが既に記入されているか確認
        if self.auth_code != '':
            is_execution = input('It looks like you already have authorization code. Do you want to run it? [y/N]').lower()
            if is_execution in ['y', 'yes']:
                pass
            elif is_execution in ['n', 'no']:
                sys.exit()
            else:
                raise ValueError('input value is "y" or "N"')

        # authorization_codeの取得
        # TODO: webbrowser.openを介した処理のテストの書き方
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(scope),
            'expires_in': expiers_in
        }
        p = urllib.parse.urlencode(params, safe='', quote_via=urllib.parse.quote)
        url = 'https://www.fitbit.com/oauth2/authorize?' + p
        webbrowser.open(url)
        self.auth_code = input('Enter authorization code (Excluding "#_=_"): ')

    def export_config(self, path: str):
        SECTION = 'FITBIT'
        config_ini = configparser.ConfigParser()
        if os.path.isfile(path):
            config_ini.read(path, encoding='utf-8')
        else:
            config_ini.add_section(SECTION)
        config_ini.set(SECTION, 'client_id', self.client_id)
        config_ini.set(SECTION, 'client_secret', self.client_secret)
        config_ini.set(SECTION, 'authorization_code', self.auth_code)
        config_ini.set(SECTION, 'access_token', self.access_token)
        config_ini.set(SECTION, 'refresh_token', self.refresh_token)
        with open(path, 'w') as configfile:
            config_ini.write(configfile)

if __name__ == '__main__':
    t = '2021-09-25'
    fb = Fitbit()
    fb.read_config('config.ini')
    fb.update_authorization_code()
    fb.update_tokens()
    fb.refresh_access_token()
    fb.export_config('config.ini')
    activities = fb.fetch_trace_data('activities', t)
    foods = fb.fetch_trace_data('foods', t)
    sleep = fb.fetch_trace_data('sleep', t)
