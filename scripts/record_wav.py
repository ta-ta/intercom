# coding: UTF-8

import os
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, '../detect'))
import detect_parameter as DETECT_PARAMETER
import microphone

# 録音秒数設定
DETECT_PARAMETER.RECORD_SECONDS = 30
# ファイル名設定
FILENAME = '../master/intercom_1.wav'

if __name__ == '__main__':
    # 録音
    microphone.set_device_index()
    if DETECT_PARAMETER.DeviceIndex < 0:
        print('cannot connect microphone:', DETECT_PARAMETER.MICROPHONE) # マイクとの接続不可
        sys.exit()

    print('filename:', FILENAME)
    print('length:', DETECT_PARAMETER.RECORD_SECONDS, 'secs')
    wave_bytes = microphone.get_wave()
    microphone.output_file(wave_bytes, filename=FILENAME)

