import json
import os
import traceback
import urllib

import pandas as pd
from pandas.tseries.offsets import DateOffset

from src.fitbit import Fitbit
from src.gcp import store_gcs
from src.health_planet import HealthPlanet


def run() -> None:
    '''実行日の前日の健康データを各APIから取得しgcsへ保存する
    '''
    # 設定
    ini_path = 'config.ini'
    day = pd.Timestamp.today(tz='Asia/Tokyo') - DateOffset(days=1)
    day_str = day.strftime('%Y-%m-%d')

    # Health Planetから体組成データを取得
    hp = HealthPlanet()
    hp.read_config(ini_path)
    body_compositions = hp.fetch_body_composition_data(day_str, day_str)

    # 体組成データを保存
    hp_path = 'data/health_planet/{}.json'.format(day_str)
    with open(hp_path, 'w') as jsonfile:
        jsonfile.write(json.dumps(body_compositions))

    # 体組成データをgcsへ転送
    try:
        store_gcs(hp_path, 'health_planet/')
        os.remove(hp_path)
    except Exception:
        print(traceback.format_exc())

    # Fitbitから運動・食事・睡眠データを取得し保存，転送
    fb = Fitbit()
    fb.read_config(ini_path)
    for c in ['activities', 'foods', 'sleep']:
        # 取得
        try:
            data = fb.fetch_trace_data(c, day_str)
        except urllib.error.HTTPError:
            print(traceback.format_exc())
            fb.refresh_access_token()
            fb.export_config(ini_path)
            data = fb.fetch_trace_data(c, day_str)

        # 保存
        fb_path = 'data/fitbit/{}/{}.json'.format(c, day_str)
        with open(fb_path, 'w') as jsonfile:
            jsonfile.write(json.dumps(data))

        # 転送
        fb_gcs_path = 'fitbit/{}/'.format(c)
        try:
            store_gcs(fb_path, fb_gcs_path)
            os.remove(fb_path)
        except Exception:
            print(traceback.format_exc())


if __name__ == '__main__':
    run()
