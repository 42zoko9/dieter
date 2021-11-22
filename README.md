# dieter
自身の身体情報をあれこれする

## Usage
事前準備
- cloud functionsを実行するサービスアカウントにsecret mangerのアクセス権限とversionの編集権限を付与する

cloud functionsへのデプロイ  
```sh
# 本プロジェクトのrootディレクトリで実行
gcloud builds submit --config ./cloudbuild.yaml . 
```