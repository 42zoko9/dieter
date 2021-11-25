import base64
import json
import re
import sys
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Fitbit:
    client_id: str
    client_secret: str
    auth_code: str = ''
    access_token: str = ''
    refresh_token: str = ''

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
        headers = {'Authorization': 'Bearer ' + self.access_token}
        url = 'https://api.fitbit.com/1.2/user/-/{category}/date/{date}.json'.format(
            category=uri_category, date=date
        )
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as e:
            print('Isnt the access token expired?  Try method "refresh_access_token".')
            raise e

        # 辞書型で出力
        return json.loads(body.decode('utf-8'))

    def create_body_log(
        self,
        body_type: str,
        value: float,
        created_date: str,
        created_time: str
    ) -> Dict[Any, Any]:
        '''指定した体組成の値をfitbitに記録する

        Args:
            body_type (str): 記録したい体組成を指定する, "weight"または"fat"のいずれかを入力
            value (float): body_typeにて指定した体組成の値
            created_date (str): 体重が記録された日付, yyyy-MM-dd
            created_time (str): 体重が記録された時間, HH:mm:ss

        Returns:
            Dict[Any, Any]: fitbitに記録したデータ
        '''
        # 引数body_typeの値確認
        if type(body_type) == str:
            if body_type not in ['weight', 'fat']:
                raise ValueError('Please input "weight" or "fat".')
        else:
            raise TypeError('"body_type" type must be str.')

        # 引数valueの値確認
        if type(value) == float:
            if value < 0:
                raise ValueError('"value" must be over 0.')
        else:
            raise TypeError('"value" type must be float or int.')

        # 引数created_dateの型確認
        if type(created_date) != str:
            raise TypeError('"created_date" type must be str.')

        # created_dateのフォーマット確認
        if not re.search(r'^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]$', created_date):
            raise ValueError('"created_date" must be yyyy-MM-dd.')

        # 引数created_timeの型確認
        if type(created_time) != str:
            raise TypeError('"created_time" type must be str.')

        # created_timeのフォーマット確認
        if not re.search(r'^[0-2][0-9]:[0-6][0-9]:[0-6][0-9]$', created_time):
            raise ValueError('"created_time" must be HH:mm:ss.')

        # 該当データを記録
        headers = {'authorization': 'Bearer ' + self.access_token}
        data = {
            body_type: value,
            'date': created_date,
            'time': created_time
        }
        url = 'https://api.fitbit.com/1/user/-/body/log/{}.json'.format(body_type)
        req = urllib.request.Request(url, headers=headers, data=urllib.parse.urlencode(data).encode())
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as e:
            print('Isnt the access token expired?  Try method "refresh_access_token".')
            raise e

        # 辞書型で出力
        return json.loads(body.decode('utf-8'))

    def refresh_access_token(self) -> None:
        '''refresh_token経由でaccess_tokenとrefresh_tokenを更新する
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
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as e:
            print('Isnt the refresh token expired? Try method "fetch_authorization_code" & "fetch_tokens".')
            raise e
        res_dict = eval(body.decode('utf-8'))
        self.access_token = res_dict['access_token']
        self.refresh_token = res_dict['refresh_token']

    def fetch_tokens(
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
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as e:
            print('Isnt the authorization code expired? Try method "fetch_authorization_code".')
            raise e
        res_dict = eval(body.decode('utf-8'))
        self.access_token = res_dict['access_token']
        self.refresh_token = res_dict['refresh_token']

    def fetch_authorization_code(
        self,
        scope: List[str] = ['activity', 'heartrate', 'location', 'nutrition', 'profile', 'settings', 'sleep', 'social', 'weight'],
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


if __name__ == '__main__':
    # 以下，ローカル環境で動作検証時に使用
    import configparser

    path = 'local.ini'
    config_ini = configparser.ConfigParser()
    config_ini.read(path, encoding='utf-8')
    client_id = config_ini.get('FITBIT', 'client-id')
    client_secret = config_ini.get('FITBIT', 'client-secret')
    access_token = config_ini.get('FITBIT', 'access-token')
    refresh_token = config_ini.get('FITBIT', 'refresh-token')

    t = '2021-09-25'
    fb = Fitbit(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        refresh_token=refresh_token
    )

    for ctg in ['activities', 'foods', 'sleep']:
        try:
            result = fb.fetch_trace_data(ctg, t)
        except urllib.error.HTTPError:
            try:
                fb.refresh_access_token()
            except urllib.error.HTTPError:
                fb.fetch_authorization_code()
                fb.fetch_tokens()
            config_ini.set('FITBIT', 'access-token', fb.access_token)
            config_ini.set('FITBIT', 'refresh-token', fb.refresh_token)
            with open(path, 'w') as f:
                config_ini.write(f)
            result = fb.fetch_trace_data(ctg, t)
        print('success: {}'.format(ctg))

    # fat = fb.create_body_log('fat', 25.6, '2021-11-01', '10:00:00')
    # pprint.pprint(fat)
    # weight = fb.create_body_log('weight', 85.0, '2021-11-01', '10:00:00')
    # pprint.pprint(weight)
