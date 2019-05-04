# coding: UTF-8

import pyaudio

# 取得する音声の設定
FORMAT = pyaudio.paInt16 # -32768 ~ +32767
CHANNELS = 1
CHUNKS = 2**10

DeviceIndex = -1

# 判定する区間の秒数
RECORD_SECONDS = 30

# 判定のための各種設定
# hash 求めるために使う設定値
SAMPLING_FREQUENCY = 11050
WINDOW_SIZE = 512
OVERLAP_RATIO = 0.75

# local_peakを取る時の近傍
PEAK_NEIGHBORHOOD_SIZE = 10
MIN_AMPLITUDE = -100

# hashを取るためのピークのペアとして考慮する長さ
FAN_VALUE = 100
MAX_HASH_TIME_DELTA = 120

# hashのマッチング後に判定結果として採用する閾値
MIN_CONFIDENCE = 70
