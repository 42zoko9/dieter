import pytest
from src.twitter import Twitter


class TestSearchRingfitadventureResults:
    '''画像のURLをまとめたリストを取得できるか検証
    - 異常系
        - dateが文字列であるが指定したフォーマットに従っていない
        - dateが実行時よりも7日以上前が与えられている
        - bearer_tokenが不適切
    - 正常系:
        - urlが格納されたリストが出力される
        - 検索条件では画像が添付されておらず空のリストが出力される
    '''
    def setup_method(self, method):
        '''各テストで共通して使用する変数を設定する
        '''
        self.fake_user_id = 'fake_user_id'
        self.fake_token = 'fake_token'

    def test_invalid_start_date_not_abide_by_format(self):
        '''検証が正しくない: dateが文字列であるが指定したフォーマットに従っていない
        '''
        # 準備
        bad_start_date = '20211108'

        # 実行・検証
        tw = Twitter(self.fake_user_id, self.fake_token)
        with pytest.raises(ValueError, match='"start_date" must be yyyy-mm-dd.'):
            tw.search_ringfitadventure_results(bad_start_date)

    def test_invalid_start_date_goes_back_more_than_7days(self):
        '''検証が正しくない: dateが実行時よりも7日以上前が与えられている
        '''
        # 準備
        bad_start_date = '2021-11-08'

        # 実行・検証
        tw = Twitter(self.fake_user_id, self.fake_token)
        with pytest.raises(ValueError, match='this method can search tweets from the last seven days'):
            tw.search_ringfitadventure_results(bad_start_date)

    @pytest.mark.skip('mockが作成できていないため')
    def test_invalid_bad_bearer_token(self):
        '''検証が正しくない: bearer_tokenが不適切
        '''
        pass

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid(self):
        '''検証が正しい: urlが格納されたリストが出力される
        '''
        pass

    @pytest.mark.skip('mockが作成できていないため')
    def test_valid_empty(self):
        '''検索条件では画像が添付されておらず空のリストが出力される
        '''
        pass
