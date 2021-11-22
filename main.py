import configparser
import json
import os
import traceback
import urllib
from typing import Union

import pandas as pd
from google.cloud import secretmanager
from pandas.tseries.offsets import DateOffset

from src.fitbit import Fitbit
from src.gcp import store_gcs
from src.health_planet import HealthPlanet


def main(event, context) -> None:
    '''cloud functions上で実行
    '''
    # GCP_PROJECT = os.getenv('GCP_PROJECT') <- python3.7のみ
    GCP_PROJECT = 'dieter-329006'
    run(GCP_PROJECT)


def run(prj: Union[None, str] = None) -> None:
    '''実行日の前日の健康データを各APIから取得しgcsへ保存する(ローカル環境で実行する場合はこちら)

    Args:
        prj (Union[None, str], optional): 関数を実行する環境，未入力(None)ならばローカルとする.
    '''
    # 設定
    print('project env: {}'.format('local' if prj is None else 'GCP'))
    additional_path = '' if prj is None else '/tmp/'
    day = pd.Timestamp.today(tz='Asia/Tokyo') - DateOffset(days=1)
    day_str = day.strftime('%Y-%m-%d')

    # 一時的にファイルを保存するディレクトリを用意(cloud functions限定)
    if prj is not None:
        os.makedirs('/tmp/data/health_planet/', exist_ok=True)
        os.makedirs('/tmp/data/fitbit/activities/', exist_ok=True)
        os.makedirs('/tmp/data/fitbit/foods/', exist_ok=True)
        os.makedirs('/tmp/data/fitbit/sleep/', exist_ok=True)

    # secret managerから値を取得
    if prj is None:
        ini_path = './local.ini'
        config_ini = configparser.ConfigParser()
        config_ini.read(ini_path, encoding='utf-8')
        api_connect_values = {
            'hp-access-token': config_ini.get('HEALTH PLANET', 'access_token'),
            'fb-client-id': config_ini.get('FITBIT', 'client_id'),
            'fb-client-secret': config_ini.get('FITBIT', 'client_secret'),
            'fb-access-token': config_ini.get('FITBIT', 'access_token'),
            'fb-refresh-token': config_ini.get('FITBIT', 'refresh_token')
        }
    else:
        secret_manager_client = secretmanager.SecretManagerServiceClient()
        api_connect_values = {}
        for k in ['hp-access-token', 'fb-client-id', 'fb-clietn-secret', 'fb-access-token', 'fb-refresh-token']:
            name = secret_manager_client.secret_version_path(prj, k, 'latest')
            response = secret_manager_client.access_secret_version(request={'name': name})
            api_connect_values[k] = response.payload.data.decode('utf-8')

    # Health Planetから体組成データを取得
    hp = HealthPlanet(
        access_token=api_connect_values['hp-access-token']
    )
    body_compositions = hp.fetch_body_composition_data(day_str, day_str)

    # 体組成データを保存
    hp_path = additional_path + 'data/health_planet/{}.json'.format(day_str)
    with open(hp_path, 'w') as jsonfile:
        jsonfile.write(json.dumps(body_compositions))

    # 体組成データをgcsへ転送
    try:
        store_gcs(hp_path, 'health_planet/{}.json'.format(day_str))
        os.remove(hp_path)
    except Exception:
        print(traceback.format_exc())

    # Fitbitから運動・食事・睡眠データを取得し保存，転送
    fb = Fitbit(
        client_id=api_connect_values['fb-client-id'],
        client_secret=api_connect_values['fb-client-secret'],
        access_token=api_connect_values['hp-access-token'],
        refresh_token=api_connect_values['fb-refresh-token']
    )
    for c in ['activities', 'foods', 'sleep']:
        # 取得
        try:
            data = fb.fetch_trace_data(c, day_str)
        except urllib.error.HTTPError:
            print('execute method "refresh_access_token"')
            fb.refresh_access_token()
            if prj is None:
                # 実行環境がローカルであればiniファイルを上書き
                config_ini.set('FITBIT', 'access_token', fb.access_token)
                config_ini.set('FITBIT', 'refresh_token', fb.refresh_token)
                with open(ini_path, 'w') as f:
                    config_ini.write(f)
            else:
                # 実行環境がcloud functions上であればsecretに新たなveersionを追加
                # NOTE: 現時点の最新versionを停止した後に再取得したトークンの値をsecretに追加する
                tmp_values = {
                    'fb-access-token': fb.access_token,
                    'fb-refresh-token': fb.refresh_token
                }
                for k in ['fb-access-token', 'fb-refresh-token']:
                    name = secret_manager_client.secret_version_path(prj, k, 'latest')
                    v_response = secret_manager_client.get_secret_version(request={'name': name})
                    response = secret_manager_client.disable_secret_version(request={'name': v_response.name})
                    parent = secret_manager_client.secret_path(prj, k)
                    response = secret_manager_client.add_secret_version(
                        request={'parent': parent, 'payload': {'data': tmp_values[k].encode('utf-8')}}
                    )
            data = fb.fetch_trace_data(c, day_str)

        # 保存
        fb_path = additional_path + 'data/fitbit/{}/{}.json'.format(c, day_str)
        with open(fb_path, 'w') as jsonfile:
            jsonfile.write(json.dumps(data))

        # 転送
        fb_gcs_path = 'fitbit/{}/{}.json'.format(c, day_str)
        try:
            store_gcs(fb_path, fb_gcs_path)
            os.remove(fb_path)
        except Exception:
            print(traceback.format_exc())


if __name__ == '__main__':
    # 以下，ローカル環境で動作検証時に使用
    run()
