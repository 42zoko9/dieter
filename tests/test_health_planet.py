import pytest
import tempfile
import configparser
from src.health_planet import HealthPlanet

class TestReadConfig:
    '''iniファイルからaccess_tokenを読み込めるか検証する
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
        self.valid_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini' ,dir='./data')
        self.valid_ini.writelines([
            '[HEALTH PLANET]\n',
            'access_token = fake_access_token'
        ])
        self.valid_ini.seek(0)

        # 検証をパスしないiniファイル作成
        self.invalid_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini' ,dir='./data')
        self.invalid_ini.writelines([
            '[HEALTH PLANET]\n',
            'invalid_access_token = fake_access_token'
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
        hp = HealthPlanet()
        with pytest.raises(TypeError, match='"path" type must be str.'):
            hp.read_config(invalid_path)

    def test_invalid_path_not_found(self):
        '''検証が正しくない: 存在しないpathを指定している
        '''
        # 準備
        invalid_path = './data/fake_dir/config.ini'

        # 実行・検証
        hp = HealthPlanet()
        with pytest.raises(ValueError, match='no such directory'):
            hp.read_config(invalid_path)

    def test_invalid_path_not_ini_file(self):
        '''検証が正しくない: 存在するファイルではあるがiniファイルではない
        '''
        # 準備
        not_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.yml' ,dir='./data')
        not_ini.seek(0)

        # 実行・検証
        hp = HealthPlanet()
        with pytest.raises(ValueError, match='"path" must be an .ini file.'):
            hp.read_config(not_ini.name)
        not_ini.close()

    def test_invalid_bad_ini(self):
        '''検証が正しくない: 読み込んだiniファイルのoptionに不正な名前が与えられている
        '''
        # 実行・検証
        hp = HealthPlanet()
        with pytest.raises(configparser.NoOptionError):
            hp.read_config(self.invalid_ini.name)

    def test_valid(self):
        '''検証が正しい: iniファイルに記載された値が各インスタンス変数に格納される
        '''
        # 実行
        hp = HealthPlanet()
        hp.read_config(self.valid_ini.name)

        # 検証
        assert hp.access_token == 'fake_access_token'

class TestFetchBodyCompositionData:
    '''体組成データを取得できるか検証
    - 異常系
        - from_dateに文字列以外の型が与えられる
        - from_dateが文字列であるが指定のフォーマットではない
        - to_dateに文字列以外の型が与えられる
        - to_dateが文字列であるが指定のフォーマットではない
        - from_dateがto_dateよりも最近の値をとる
        - from_dateに現時点より3ヶ月前の日付が与えられている
        - access_tokenが不適切
    - 正常系: 体組成データを取得する
        - 指定した期間内のデータが含まれている
        - データが空
    '''
    def setup_method(self, method):
        '''検証に使用するデータを生成する
        '''
        # 検証にパスするiniファイル作成
        self.fake_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini' ,dir='./data')
        self.fake_ini.writelines([
            '[HEALTH PLANET]\n',
            'access_token = fake_access_token'
        ])
        self.fake_ini.seek(0)

        # 検証をパスしないiniファイル作成
        self.fake_bad_ini = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', suffix='.ini' ,dir='./data')
        self.fake_bad_ini.writelines([
            '[HEALTH PLANET]\n',
            'invalid_access_token = fake_access_token'
        ])
        self.fake_bad_ini.seek(0)

    def teardown_method(self, method):
        '''ダミーのiniファイル削除
        '''
        self.fake_ini.close()
        self.fake_bad_ini.close()

    def test_invalid_from_date_not_string(self):
        '''from_dateに文字列以外の型が与えられる
        '''
        # 準備
        invalid_from_date = 20210925
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        with pytest.raises(TypeError, match='"from_date" type must be str.'):
            hp.fetch_body_composition_data(invalid_from_date, fake_to_date)

    def test_invalid_from_date_not_abide_by_format(self):
        '''検証が正しくない: from_dateが文字列であるが指定のフォーマットではない
        '''
        # 準備
        invalid_from_date = '20210925'
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='"from_date" must be yyyy-mm-dd.'):
            hp.fetch_body_composition_data(invalid_from_date, fake_to_date)

    def test_invalid_to_date_not_string(self):
        '''検証が正しくない: from_dateに文字列以外の型が与えられる
        '''
        # 準備
        fake_from_date = '2021-09-25'
        invalid_to_date = 20210925

        # 実行・検証
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        with pytest.raises(TypeError, match='"to_date" type must be str.'):
            hp.fetch_body_composition_data(fake_from_date, invalid_to_date)

    def test_invalid_to_date_not_abide_by_format(self):
        '''検証が正しくない: from_dateが文字列であるが指定のフォーマットではない
        '''
        # 準備
        fake_from_date = '2021-09-25'
        invalid_to_date = '20210925'

        # 実行・検証
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='"to_date" must be yyyy-mm-dd.'):
            hp.fetch_body_composition_data(fake_from_date, invalid_to_date)

    def test_invalid_from_date_geq_to_date(self):
        '''検証が正しくない: from_dateがto_dateよりも最近の値をとる
        '''
        # 準備
        invalid_from_date = '2021-09-26'
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        with pytest.raises(ValueError, match='"to_date" is greater than "from_date".'):
            hp.fetch_body_composition_data(invalid_from_date, fake_to_date)

    def test_invalid_from_date_over_3month_ago(self):
        '''検証が正しくない: from_dateに現時点より3ヶ月前の日付が与えられている
        '''
        # 準備
        invalid_from_date = '2021-05-25'
        fake_to_date = '2021-09-25'

        # 実行・検証
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
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
    def test_valid_contained_data(self):
        '''[summary]
        '''
        # 準備
        fake_from_date = '2021-09-28'
        fake_to_date = '2021-09-28'

        # 実行
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        data = hp.fetch_body_composition_data(fake_from_date, fake_to_date)

    # TODO: mockの作成方法
    @pytest.mark.skip('mockが作成できていないため')
    def test_valid_contained_data(self):
        '''[summary]
        '''
        # 準備
        fake_from_date = '2021-09-29'
        fake_to_date = '2021-09-29'

        # 実行
        hp = HealthPlanet()
        hp.read_config(self.fake_ini.name)
        data = hp.fetch_body_composition_data(fake_from_date, fake_to_date)
