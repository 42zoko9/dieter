import urllib

import pytest
from src.fitbit import Fitbit


@pytest.mark.skip('input()やwebbrowser.open()を含む処理のテストの書き方')
class TestFetchAuthorizationCode:
    '''authorization codeを取得できるかテストする
    - 異常系
        - scopeがlist以外で与えられている
        - scopeのlistの中に不正な文字列が混入している
        - expiers_inがint以外で与えられている
        - expiers_inに0以下の値が与えられる
        - redicret_idが文字列ではない
        - redirect_uriがURIの形をとっていない
        - client_idの入力にて間違った入力をする
        - client_secretの入力にて間違った入力をする
    - 正常系: `auth_code`に取得したURIに付与された値が格納される
    '''
    def setup_method(self, method):
        '''検証に使用するダミーのclientIdとclientSecretを用意する
        '''
        self.fake_client_id = 'fake_client_id'
        self.fake_client_secret = 'fake_client_secret'

    def test_invalid_scope_not_list(self):
        '''検証が正しくない: scopeがlist以外で与えられている
        '''
        pass

    def test_invalid_scope_contain_not_string(self):
        '''検証が正しくない: scopeのlistの中に不正な文字列が混入している
        '''
        pass

    def test_invalid_expiers_in_not_int(self):
        '''検証が正しくない: expiers_inがint以外で与えられている
        '''
        pass

    def test_invalid_expiers_in_leq_zero(self):
        '''検証が正しくない: expiers_inに0以下の値が与えられる
        '''
        pass

    def test_invalid_redirect_uri_not_string(self):
        '''検証が正しくない: redicret_idが文字列ではない
        '''
        pass

    def test_invalid_redirect_uri_not_uri_format(self):
        '''検証が正しくない: redirect_uriがURIの形をとっていない
        '''
        pass

    def test_invalid_client_id_typing_err(self):
        '''検証が正しくない: client_idの入力にて間違った入力をする
        '''
        pass

    def test_invalid_client_secret_typing_err(self):
        '''検証が正しくない: client_secretの入力にて間違った入力をする
        '''
        pass

    def test_valid(self):
        '''検証が正しい
        '''
        pass


# TODO: authorization_codeが不正の場合にErrorを返すmockの作成方法
class TestFetchTokens:
    '''access_tokenとrefresh_tokenを取得し更新できるかを検証
    - 異常系
        - redirect_uriが文字列以外の型で与えられる
        - redirect_uriが文字列であるがuriのフォーマットに従っていない
        - auth_codeが未取得もしくは期限切れである
    - 正常系: access_tokenとrefresh_tokenの値が更新される
    '''
    def setup_method(self, method):
        '''検証に使用するダミーのclientIdとclientSecret, authorizationCodeを用意する
        '''
        self.fake_client_id = 'fake_client_id'
        self.fake_client_secret = 'fake_client_secret'
        self.fake_auth_code = 'fake_auth_code'

    def test_invalid_redirect_uri_not_string(self):
        '''検証が正しくない: redirect_uriが文字列以外で与えられている
        '''
        # 準備
        invalid_redirect_uri = int(71)

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            auth_code=self.fake_auth_code
        )
        with pytest.raises(TypeError, match='"redirect_uri" type must be str.'):
            fb.fetch_tokens(invalid_redirect_uri)

    def test_invalid_redirect_uri_not_uri_format(self):
        '''検証が正しくない: redirect_uriがuriのフォーマットに従っていない
        '''
        # 準備
        invalid_redirect_uri = 'not_uri_format_string'

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            auth_code=self.fake_auth_code
        )
        with pytest.raises(ValueError, match='"redirect_uri" must be a uri format.'):
            fb.fetch_tokens(invalid_redirect_uri)

    def test_invalid_bad_auth_code(self):
        '''検証が正しくない: auth_codeが不正な値が与えられている
        '''
        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            auth_code=self.fake_auth_code
        )
        with pytest.raises(urllib.error.HTTPError, match='HTTP Error 401: Unauthorized'):
            fb.fetch_tokens()

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid(self):
        '''検証が正しい: access_tokenとrefresh_tokenの値が更新される
        '''
        pass


# TODO: refresh_tokenが不正の場合にErrorを返すmockの作成方法
class TestRefreshAccessToken:
    '''refresh_tokenを用いた手続きよりaccess_tokenを再取得できるか検証
    - 異常系
        - refresh_tokenの値が期限切れもしくは誤っている
    - 正常系: access_tokenとrefresh_tokenが新しい値に更新される
    '''
    def setup_method(self, method):
        '''検証に使用するダミーのclientIdとclientSecret, refreshTokenを用意する
        '''
        self.fake_client_id = 'fake_client_id'
        self.fake_client_secret = 'fake_client_secret'
        self.bad_access_token = 'bad_access_token'
        self.fake_refresh_token = 'fake_refresh_token'

    def test_invalid_bad_refresh_token(self):
        '''検証が正しくない: refresh_tokenが期限切れもしくは誤っている
        '''
        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.bad_access_token,
            refresh_token=self.fake_refresh_token
        )
        with pytest.raises(urllib.error.HTTPError, match='HTTP Error 401: Unauthorized'):
            fb.refresh_access_token()

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid(self):
        '''検証が正しい: access_tokenとrefresh_tokenが新しい値に更新される
        '''
        pass


# TODO: access_tokenが不正の場合にErrorを返すmockの作成方法
class TestFetchTraceData:
    '''指定した日付とカテゴリのトレースデータが出力できているかテストする
    - 異常系
        - categoryに文字列以外の型が与えられる
        - categoryにて"activities", "foods", "sleep"以外の値が与えられる
        - dateに文字列以外の型が与えられる
        - dateが文字列であるが指定したフォーマットに従っていない
        - access_tokenが期限切れ
    - 正常系
        - 指定した日にちの"activities"データを取得する
        - 指定した日にちの"foods"データを取得する
        - 指定した日にちの"sleep"データを取得する
    '''
    def setup_method(self, method):
        '''検証に使用するダミーのclientIdとclientSecret, refreshTokenを用意する
        '''
        self.fake_client_id = 'fake_client_id'
        self.fake_client_secret = 'fake_client_secret'
        self.fake_access_token = 'fake_access_token'
        self.bad_access_token = 'bad_access_token'

    def test_invalid_category_not_string(self):
        '''検証が正しくない: categoryに文字列以外の型が与えられる
        '''
        # 準備
        fake_date = '2021-09-25'
        invalid_category = 71

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.fake_access_token
        )
        with pytest.raises(TypeError, match='"category" type must be str.'):
            fb.fetch_trace_data(invalid_category, fake_date)

    def test_invalid_category_bad_string(self):
        '''検証が正しくない: categoryにて"activities", "foods", "sleep"以外の値が与えられる
        '''
        # 準備
        fake_date = '2021-09-25'
        invalid_category = 'fake_category'

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.fake_access_token
        )
        with pytest.raises(ValueError, match='Please input "activities" or "foods" or "sleep"'):
            fb.fetch_trace_data(invalid_category, fake_date)

    def test_invalid_date_not_string(self):
        '''検証が正しくない: dateに文字列以外の型が与えられる
        '''
        # 準備
        fake_category = 'activities'
        invalid_date = 20210925

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.fake_access_token
        )
        with pytest.raises(TypeError, match='"date" type must be str.'):
            fb.fetch_trace_data(fake_category, invalid_date)

    def test_invalid_date_not_abide_by_format(self):
        '''検証が正しくない: dateが文字列であるが指定したフォーマットに従っていない
        '''
        # 準備
        fake_category = 'activities'
        invalid_date = '20210925'

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.fake_access_token
        )
        with pytest.raises(ValueError, match='"date" must be yyyy-mm-dd.'):
            fb.fetch_trace_data(fake_category, invalid_date)

    def test_invalid_access_token_is_expired(self):
        '''検証が正しくない: access_tokenの期限切れ
        '''
        # 準備
        fake_category = 'activities'
        fake_date = '2021-09-25'

        # 実行・検証
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.bad_access_token
        )
        with pytest.raises(urllib.error.HTTPError, match='HTTP Error 401: Unauthorized'):
            fb.fetch_trace_data(fake_category, fake_date)

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid_activities(self):
        '''検証が正しい: 指定した日にちの"activities"データを取得する
        '''
        pass

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid_foods(self):
        '''検証が正しい: 指定した日にちの"foods"データを取得する
        '''
        pass

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid_sleep(self):
        '''検証が正しい: 指定した日にちの"sleep"データを取得する
        '''
        pass


# TODO: access_tokenが不正の場合にErrorを返すmockの作成方法
# TODO: データを書き込む系のAPIの検証方法
class TestCreateBodyLog:
    '''
    - 異常系
        - body_typeに文字列以外の型が与えられる
        - body_typeにて"fat", "weight"以外の値が与えられる
        - valueにfloat以外の型が与えられる
        - valueに異常な値(0未満)が与えられる
        - created_dateに文字列以外の型が与えられる
        - created_dateが文字列であるが指定したフォーマットに従っていない
        - created_timeに文字列以外の型が与えられる
        - created_timeが文字列であるが指定したフォーマットに従っていない
        - 生成したtokenにweightのアクセス権限が付与されていない
        - access_tokenの期限切れ
    - 正常系:
        - 指定した日時の"weight"が入力される
        - 指定した日時の"fat"が入力される
    '''
    def setup_method(self, method):
        self.fake_client_id = 'fake_client_id'
        self.fake_client_secret = 'fake_client_secret'
        self.denied_access_token = 'denied_access_token'
        self.expierd_access_token = 'expired_access_token'
        self.fake_access_token = 'fake_access_token'

    def test_invalid_body_type_not_string(self):
        '''検証が正しくない: body_typeに文字列以外の型が与えられる
        '''
        pass

    def test_invalid_body_type_not_abide_by_format(self):
        '''検証が正しくない: body_typeにて"fat", "weight"以外の値が与えられる
        '''
        pass

    def test_invalid_value_not_float(self):
        '''検証が正しくない: valueにfloat以外の型が与えられる
        '''
        pass

    def test_invalid_value_leq_zero(self):
        '''検証が正しくない: valueに異常な値(0未満)が与えられる
        '''
        pass

    def test_invalid_created_date_not_string(self):
        '''検証が正しくない: created_dateに文字列以外の型が与えられる
        '''
        pass

    def test_invalid_creatd_date_not_abide_by_format(self):
        '''検証が正しくない: created_dateにて"fat", "weight"以外の値が与えられる
        '''
        pass

    def test_invalid_created_time_not_string(self):
        '''検証が正しくない: created_dateに文字列以外の型が与えられる
        '''
        pass

    def test_invalid_creatd_time_not_abide_by_format(self):
        '''検証が正しくない: created_dateにて"fat", "weight"以外の値が与えられる
        '''
        pass

    @pytest.mark.skip('これまで抜けていた観点, 今後検証する必要あり')
    def test_invalid_permission_denied(self):
        '''検証が正しくない: 生成したtokenにprofileのアクセス権限が付与されていない
        '''
        pass

    def test_invalid_access_token_epierd(self):
        '''検証が正しくない: access_tokenの期限切れ
        '''
        fake_body_type = 'fat'
        fake_value = 25.1
        fake_date = '2021-11-01'
        fake_time = '13:00:01'
        fb = Fitbit(
            client_id=self.fake_client_id,
            client_secret=self.fake_client_secret,
            access_token=self.expierd_access_token
        )
        with pytest.raises(urllib.error.HTTPError, match='HTTP Error 401: Unauthorized'):
            fb.create_body_log(
                fake_body_type, fake_value, fake_date, fake_time
            )

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid(self):
        '''検証が正しい: プロフィールが格納された辞書型のデータを取得する
        '''
        pass
