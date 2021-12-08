import pytest
from src.health_planet import HealthPlanet


class TestFetchBodyCompositionData:
    '''体組成データを取得できるか検証
    - 異常系
        - from_dateが文字列であるが指定のフォーマットではない
        - to_dateが文字列であるが指定のフォーマットではない
        - from_dateがto_dateよりも最近の値をとる
        - from_dateに現時点より3ヶ月前の日付が与えられている
        - access_tokenが不適切
    - 正常系: 体組成データを取得する

    '''
    def setup_method(self, method):
        '''検証に使用するダミーのアクセストークン を設定
        '''
        self.fake_access_token = 'fake_access_token'
        self.bad_access_token = 'bad_access_token'

    def test_invalid_from_date_not_abide_by_format(self):
        '''検証が正しくない: from_dateが文字列であるが指定のフォーマットではない
        '''
        # 準備
        invalid_from_date = '20210925'
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet(self.fake_access_token)
        with pytest.raises(ValueError, match='"from_date" must be yyyy-mm-dd.'):
            hp.fetch_body_composition_data(invalid_from_date, fake_to_date)

    def test_invalid_to_date_not_abide_by_format(self):
        '''検証が正しくない: from_dateが文字列であるが指定のフォーマットではない
        '''
        # 準備
        fake_from_date = '2021-09-25'
        invalid_to_date = '20210925'

        # 実行・検証
        hp = HealthPlanet(self.fake_access_token)
        with pytest.raises(ValueError, match='"to_date" must be yyyy-mm-dd.'):
            hp.fetch_body_composition_data(fake_from_date, invalid_to_date)

    def test_invalid_from_date_geq_to_date(self):
        '''検証が正しくない: from_dateがto_dateよりも最近の値をとる
        '''
        # 準備
        invalid_from_date = '2021-09-26'
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet(self.fake_access_token)
        with pytest.raises(ValueError, match='"to_date" is greater than "from_date".'):
            hp.fetch_body_composition_data(invalid_from_date, fake_to_date)

    def test_invalid_from_date_over_3month_ago(self):
        '''検証が正しくない: from_dateに現時点より3ヶ月前の日付が与えられている
        '''
        # 準備
        invalid_from_date = '2021-05-25'
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet(self.fake_access_token)
        with pytest.raises(ValueError, match='"from_date" is over 3 month ago.'):
            hp.fetch_body_composition_data(invalid_from_date, fake_to_date)

    # TODO: access_tokenが不適切な場合Errorを返すmockの作成方法
    @pytest.mark.skip('mockが作成できていないため')
    def test_invalid_bad_access_token(self):
        '''検証が正しくない: access_tokenが不適切
        '''
        pass

    # TODO: mockの作成方法
    @pytest.mark.skip('mockが作成できていないため')
    def test_valid(self):
        '''検証が正しい: 体組成データを取得する
        '''
        # 準備
        fake_from_date = '2021-09-28'
        fake_to_date = '2021-09-28'

        # 実行
        hp = HealthPlanet(self.fake_access_token)
        hp.fetch_body_composition_data(fake_from_date, fake_to_date)
