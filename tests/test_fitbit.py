import configparser
import os
import tempfile

import pytest
from src.fitbit import Fitbit


class TestReadConfig:
    '''read_configメソッドのテスト
    - 異常系
        - pathが文字列以外の型で与えられる
        - 存在しないpathを指定している
        - 存在するファイルではあるがiniファイルではない
        - 読み込んだiniファイルのoptionに不正な名前が与えられている
    - 正常系: iniファイルに記載された値が各インスタンス変数に格納される
    '''
    def setup_method(self, method):
        '''検証に使用するデータを生成する
        '''
        # 検証にパスするiniファイル作成
        self.valid_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini', dir='./data')
        self.valid_ini.writelines([
            '[FITBIT]\n',
            'client_id = fake_client_id\n',
            'client_secret = fake_client_secret\n',
            'authorization_code = fake_auth_code\n',
            'access_token = fake_access_token\n',
            'refresh_token = fake_refresh_token\n'
        ])
        self.valid_ini.seek(0)

        # 検証をパスしないiniファイル作成
        self.invalid_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini', dir='./data')
        self.invalid_ini.writelines([
            '[FITBIT]\n',
            'client_id = invalid_fake_client_id\n',
            'client_secret = invalid_fake_client_secret\n',
            'auth = invalid_fake_auth_code\n',
            'access_token = invalid_fake_access_token\n',
            'refresh_token = invalid_fake_refresh_token\n'
        ])
        self.invalid_ini.seek(0)

    def teardown_method(self, method):
        '''ダミーのiniファイル削除
        '''
        self.valid_ini.close()
        self.invalid_ini.close()

    def test_invalid_path_not_string(self):
        '''検証が正しくない: pathが文字列以外の型で与えられる
        '''
        # 準備
        invalid_path = 71

        # 実行・検証
        fb = Fitbit()
        with pytest.raises(TypeError, match='"path" type must be str.'):
            fb.read_config(invalid_path)

    def test_invalid_path_not_found(self):
        '''検証が正しくない: 存在しないpathを指定している
        '''
        # 準備
        invalid_path = './data/fake_dir/config.ini'

        # 実行・検証
        fb = Fitbit()
        with pytest.raises(ValueError, match='no such directory'):
            fb.read_config(invalid_path)

    def test_invalid_path_not_ini_file(self):
        '''検証が正しくない: 存在するファイルではあるがiniファイルではない
        '''
        # 準備
        not_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.yml', dir='./data')
        not_ini.seek(0)

        # 実行・検証
        fb = Fitbit()
        with pytest.raises(ValueError, match='"path" must be an .ini file.'):
            fb.read_config(not_ini.name)
        not_ini.close()

    def test_invalid_bad_ini(self):
        '''検証が正しくない: 読み込んだiniファイルのoptionに不正な名前が与えられている
        '''
        # 実行・検証
        fb = Fitbit()
        with pytest.raises(configparser.NoOptionError):
            fb.read_config(self.invalid_ini.name)

    def test_valid(self):
        '''検証が正しい: iniファイルに記載された値が各インスタンス変数に格納される
        '''
        # 実行
        fb = Fitbit()
        fb.read_config(self.valid_ini.name)

        # 検証
        assert fb.client_id == 'fake_client_id'
        assert fb.client_secret == 'fake_client_secret'
        assert fb.auth_code == 'fake_auth_code'
        assert fb.access_token == 'fake_access_token'
        assert fb.refresh_token == 'fake_refresh_token'


# TODO: input()やwebbrowser.open()を含む処理のテストの書き方
class TestUpdateAuthorizationCode:
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
        '''検証に使用するデータを生成する
        '''
        # 検証にパスするiniファイル作成
        self.fake_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini', dir='./data')
        self.fake_ini.writelines([
            '[FITBIT]\n',
            'client_id = fake_client_id\n',
            'client_secret = fake_client_secret\n',
            'authorization_code = fake_auth_code\n',
            'access_token = fake_access_token\n',
            'refresh_token = fake_refresh_token\n'
        ])
        self.fake_ini.seek(0)

    def teardown_method(self, method):
        '''ダミーのiniファイル削除
        '''
        self.fake_ini.close()

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
class TestUpdateTokens:
    '''access_tokenとrefresh_tokenを取得し更新できるかを検証
    - 異常系
        - redirect_uriが文字列以外の型で与えられる
        - redirect_uriが文字列であるがuriのフォーマットに従っていない
        - auth_codeが未取得もしくは期限切れである
    - 正常系: access_tokenとrefresh_tokenの値が更新される
    '''
    def setup_method(self, method):
        '''検証に使用するデータを生成する
        '''
        # 検証にパスするiniファイル作成
        self.fake_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini', dir='./data')
        self.fake_ini.writelines([
            '[FITBIT]\n',
            'client_id = fake_client_id\n',
            'client_secret = fake_client_secret\n',
            'authorization_code = fake_auth_code\n',
            'access_token = \n',
            'refresh_token = \n'
        ])
        self.fake_ini.seek(0)

    def teardown_method(self, method):
        '''ダミーのiniファイル削除
        '''
        self.fake_ini.close()

    def test_invalid_redirect_uri_not_string(self):
        '''検証が正しくない: redirect_uriが文字列以外で与えられている
        '''
        # 準備
        invalid_redirect_uri = int(71)

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(TypeError, match='"redirect_uri" type must be str.'):
            fb.update_tokens(invalid_redirect_uri)

    def test_invalid_redirect_uri_not_uri_format(self):
        '''検証が正しくない: redirect_uriがuriのフォーマットに従っていない
        '''
        # 準備
        invalid_redirect_uri = 'not_uri_format_string'

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='"redirect_uri" must be a uri format.'):
            fb.update_tokens(invalid_redirect_uri)

    def test_invalid_bad_auth_code(self):
        '''検証が正しくない: auth_codeが不正な値が与えられている
        '''
        pass

    def test_valid(self):
        '''検証が正しい: access_tokenとrefresh_tokenの値が更新される
        '''
        pass


# TODO: refresh_tokenが不正の場合にErrorを返すmockの作成方法
class TestRefreshAccessToken:
    '''refresh_tokenを用いた手続きよりaccess_tokenを再取得できるか検証
    - 異常系
        - refresh_tokenの値が期限切れもしくは謝っている
    - 正常系: access_tokenが新しい値に更新される
    '''

    def test_invalid_bad_refresh_token(self):
        '''検証が正しくない: refresh_tokenが期限切れもしくは誤っている
        '''
        pass

    def test_valid(self):
        '''検証が正しい: access_tokenが新しい値に更新される
        '''
        pass


# TODO: 外部に結果を出力する場合のテストの書き方
class TestExportConfig:
    '''各インスタンス変数をiniファイルに出力できるか検証
    - 異常系
        - pathに文字列以外の型が与えられる
        - pathが存在しないフォルダを指している
        - pathの末尾が`.ini`でない
    - 正常系: 各インスタンス変数の値がiniファイルに書き出される
    '''
    def setup_method(self, method):
        '''検証に使用するデータを生成する
        '''
        # 検証にパスするiniファイル作成
        self.fake_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini', dir='./data')
        self.fake_ini.writelines([
            '[FITBIT]\n',
            'client_id = fake_client_id\n',
            'client_secret = fake_client_secret\n',
            'authorization_code = fake_auth_code\n',
            'access_token = fake_access_token\n',
            'refresh_token = fake_refresh_token\n'
        ])
        self.fake_ini.seek(0)

    def teardown_method(self, method):
        '''ダミーのiniファイル削除
        '''
        self.fake_ini.close()

    def test_invalid_path_not_string(self):
        '''検証が正しくない: pathに文字列以外の型が与えられる
        '''
        # 準備
        invalid_path = 71

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(TypeError, match='"path" type must be str.'):
            fb.export_config(invalid_path)

    def test_invalid_path_not_found(self):
        '''検証が正しくない: pathが存在しないフォルダを指している
        '''
        # 準備
        invalid_path = './data/fake/fake_config.ini'

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='no such directory'):
            fb.export_config(invalid_path)

    def test_invalid_path_not_ini(self):
        '''検証が正しくない: pathの末尾が`.ini`でない
        '''
        # 準備
        invalid_path = 'data/fake_config.yml'

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='"path" must be an .ini file.'):
            fb.export_config(invalid_path)

    # TODO: ファイル出力のテスト方法
    def test_valid(self):
        '''検証が正しい: 各インスタンス変数の値がiniファイルに書き出される
        '''
        # 準備
        valid_ini = 'data/fake_config.ini'

        # 実行
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        fb.export_config(valid_ini)

        # 検証
        validate_fb = Fitbit()
        validate_fb.read_config(valid_ini)
        assert validate_fb.client_id == 'fake_client_id'
        assert validate_fb.client_secret == 'fake_client_secret'
        assert validate_fb.auth_code == 'fake_auth_code'
        assert validate_fb.access_token == 'fake_access_token'
        assert validate_fb.refresh_token == 'fake_refresh_token'

        # 出力ファイルを削除
        os.remove(valid_ini)


# TODO: access_tokenが不正の場合にErrorを返すmockの作成方法
class TestFetchTraceData:
    '''指定した日付とカテゴリのトレースデータが出力できているかテストする
    - 異常系
        - categoryに文字列以外の型が与えられる
        - categoryにて"activities", "foods", "sleep"以外の値が与えられる
        - dateに文字列以外の型が与えられる
        - dateが文字列であるが指定したフォーマットに従っていない
    - 正常系
        - access_tokenが不適切であった場合，refresh_tokenを介してデータを取得する
        - 指定した日にちの"activities"データを取得する
        - 指定した日にちの"foods"データを取得する
        - 指定した日にちの"sleep"データを取得する
    '''
    def setup_method(self, method):
        '''検証に使用するデータを生成する
        '''
        # 検証にパスするiniファイル作成
        self.fake_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini', dir='./data')
        self.fake_ini.writelines([
            '[FITBIT]\n',
            'client_id = fake_client_id\n',
            'client_secret = fake_client_secret\n',
            'authorization_code = fake_auth_code\n',
            'access_token = fake_access_token\n',
            'refresh_token = fake_refresh_token\n'
        ])
        self.fake_ini.seek(0)

    def teardown_method(self, method):
        '''ダミーのiniファイル削除
        '''
        self.fake_ini.close()

    def test_invalid_category_not_string(self):
        '''検証が正しくない: categoryに文字列以外の型が与えられる
        '''
        # 準備
        fake_date = '2021-09-25'
        invalid_category = 71

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(TypeError, match='"category" type must be str.'):
            fb.fetch_trace_data(invalid_category, fake_date)

    def test_invalid_category_bad_string(self):
        '''検証が正しくない: categoryにて"activities", "foods", "sleep"以外の値が与えられる
        '''
        # 準備
        fake_date = '2021-09-25'
        invalid_category = 'fake_category'

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='Please input "activities" or "foods" or "sleep"'):
            fb.fetch_trace_data(invalid_category, fake_date)

    def test_invalid_date_not_string(self):
        '''検証が正しくない: dateに文字列以外の型が与えられる
        '''
        # 準備
        fake_category = 'activities'
        invalid_date = 20210925

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(TypeError, match='"date" type must be str.'):
            fb.fetch_trace_data(fake_category, invalid_date)

    def test_invalid_date_not_abide_by_format(self):
        '''検証が正しくない: dateが文字列であるが指定したフォーマットに従っていない
        '''
        # 準備
        fake_category = 'activities'
        invalid_date = '20210925'

        # 実行・検証
        fb = Fitbit()
        fb.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='"date" must be yyyy-mm-dd.'):
            fb.fetch_trace_data(fake_category, invalid_date)

    def test_invalid_refresh_token_not_used(self):
        '''検証が正しくない: refresh_tokenが機能せずaccess_tokenが更新できない
        '''
        pass

    # NOTE: refresh_access_token()メソッドを実行することになるため，これは結合テストとなる？
    def test_valid_access_token_not_used(self):
        '''検証が正しい: access_tokenが不適切であった場合，refresh_tokenを介してデータを取得する
        '''
        pass

    def test_valid_activities(self):
        '''検証が正しい: 指定した日にちの"activities"データを取得する
        '''
        pass

    def test_valid_foods(self):
        '''検証が正しい: 指定した日にちの"foods"データを取得する
        '''
        pass

    def test_valid_sleep(self):
        '''検証が正しい: 指定した日にちの"sleep"データを取得する
        '''
        pass
