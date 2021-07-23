from fetch_body_composition import fetch_body_composition
import pandas as pd
from pandas.tseries.offsets import DateOffset
from datetime import datetime
import pytest
import configparser
import urllib

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
actual_token = config_ini.get('DEFAULT', 'hp_access_token')
wrong_token = 'xxxxxxxx'

to_dt = pd.Timestamp.today(tz='Asia/Tokyo')
from_dt = to_dt - DateOffset(months=1)
to_date = to_dt.strftime('%Y%m%d')
from_date = from_dt.strftime('%Y%m%d')

from_3Mago_dt = to_dt - DateOffset(months=3) - DateOffset(days=1)
from_3Mago_date = from_3Mago_dt.strftime('%Y%m%d')

from_future_dt = to_dt + DateOffset(months=1)
to_future_dt = from_future_dt + DateOffset(months=1)
to_future_date = to_future_dt.strftime('%Y%m%d')
from_future_date = from_future_dt.strftime('%Y%m%d')

class TestBodyComposition:
    
    @pytest.mark.parametrize('token, from_date, to_date', [(actual_token, from_date, to_date)])
    def test_correct_params(self, token:str, from_date:str, to_date:str) -> None:
        '''パラメータが正しく与えられた場合
        '''
        assert datetime.strptime(from_date, '%Y%m%d') <= datetime.strptime(to_date, '%Y%m%d')

        result = fetch_body_composition(token, from_date, to_date)
        assert len(result) >= 2

        key_macth_len = sum([set(_) == {'date', 'keydata', 'model', 'tag'} for _ in result])
        assert len(result) == key_macth_len
    
    @pytest.mark.parametrize('token, from_date, to_date', [(actual_token, from_3Mago_date, to_date)])
    def test_fetched_prediod_gt_3M(self, token:str, from_date:str, to_date:str) -> None:
        '''データの取得期間が3ヶ月以内でない場合
        '''
        with pytest.raises(Exception, match='from_date is over 3 month ago'):
            fetch_body_composition(token, from_date, to_date)

    @pytest.mark.parametrize('token, from_date, to_date', [(actual_token, to_date, from_date)])
    def test_fromd_gt_tod(self, token:str, from_date:str, to_date:str) -> None:
        '''from_dateがto_dateよりも大きい場合
        '''
        with pytest.raises(urllib.error.HTTPError):
            fetch_body_composition(token, from_date, to_date)

    @pytest.mark.parametrize('token, from_date, to_date', [(actual_token, from_future_date, to_future_date)])
    def test_empty_result(self, token:str, from_date:str, to_date:str) -> None:
        '''出力されるデータが空の場合(取得期間が未来の場合)
        '''
        with pytest.raises(Exception, match='fetched data is empty'):
            fetch_body_composition(token, from_date, to_date)

    @pytest.mark.parametrize('token, from_date, to_date', [(wrong_token, from_date, to_date)])
    def test_incorrect_token(self, token:str, from_date:str, to_date:str) -> None:
        '''アクセストークンが誤っている場合
        '''
        with pytest.raises(urllib.error.HTTPError):
            fetch_body_composition(token, from_date, to_date)
