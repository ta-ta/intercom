# 概要
マイクから音声を取得して、あらかじめmasterに登録しておいた楽曲との判定を行う。  
判定できた場合は、slackに通知する。  

# 準備
1. `scripts/record_wav.py` によって録音する。  
    録音時間と保存先を設定
2. `scripts/add_master.py` によってmasterにfingerprintを登録する。  
    wavファイルを指定する

# 実行
`python3 main.py`で実行可能
以下のファイルの設定を確認しておく
- `env/local.py`
- `detect_parameter.py`

## 判定アルゴリズム
- `detect.py`
- `fingerprint.py`
