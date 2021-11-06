import json
import traceback
import urllib

import pandas as pd
from pandas.tseries.offsets import DateOffset

from src.fitbit import Fitbit
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
    path_jsonfile = 'data/health_planet/{}.json'.format(day_str)
    with open(path_jsonfile, 'w') as jsonfile:
        jsonfile.write(json.dumps(body_compositions))

    # Fitbitから運動・食事・睡眠データを取得し保存
    fb = Fitbit()
    fb.read_config(ini_path)
    for c in ['activities', 'foods', 'sleep']:
        try:
            data = fb.fetch_trace_data(c, day_str)
        except urllib.error.HTTPError:
            print(traceback.format_exc())
            fb.refresh_access_token()
            fb.export_config(ini_path)
            data = fb.fetch_trace_data(c, day_str)

        path_jsonfile = 'data/fitbit/{}/{}.json'.format(c, day_str)
        with open(path_jsonfile, 'w') as jsonfile:
            jsonfile.write(json.dumps(data))


if __name__ == '__main__':
    run()
