import configparser
from dataclasses import dataclass
from typing import List, Dict, Any, Type
import os
import re
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

    def read_config(self, path: str) -> None:
        '''FITBIT周りの環境変数が記述されたiniファイルを読み込み各インスタンス変数に代入する

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
        '''fitbitからトレースデータを取得し辞書型で出力

        Args:
            category (str): "activities", "foods", "sleep"のいずれかを入力
            date (str): 取得したいデータの日付, "yyyy-mm-dd"形式で入力

        Returns:
            Dict[Any, Any]: 取得データ
        '''
        # 引数categoryの型確認
        if type(category) != str:
            raise TypeError('"category" type must be str.')

        # categoryの前処理
        if category == 'activities':
            uri_category = category
        elif category == 'foods':
            uri_category = 'foods/log'
        elif category == 'sleep':
            uri_category = category
        else:
            raise ValueError('Please input "activities" or "foods" or "sleep"')

        # 引数dateの型確認
        if type(date) != str:
            raise TypeError('"date" type must be str.')
        
        # dateのフォーマット確認
        if not re.search(r'^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]$', date):
            raise ValueError('"date" must be yyyy-mm-dd.')

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
        # 引数の型確認
        if type(redirect_uri) != str:
            raise TypeError('"redirect_uri" type must be str.')

        # 引数の文字列フォーマット確認
        if not re.search(r'^http(|s)://.+$', redirect_uri):
            raise ValueError('"redirect_uri" must be a uri format.')

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
        # TODO: input関数を使用している場合のテストの書き方
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

    def export_config(self, path: str) -> None:
        '''各インスタンス変数をiniファイルに出力する

        Args:
            path (str): 出力ファイルのパス名
        '''
        # 引数の型確認
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

        # iniファイルへの書き込み
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
