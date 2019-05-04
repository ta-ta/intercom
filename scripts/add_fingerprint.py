# coding: UTF-8

import os
import sys



PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, '../detect'))
import fingerprint
import env.local as CONFIG
import decoder

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, '../db'))
import mysql_intercom

# 対象wavファイルを設定
TARGET_FILES = ['../master/intercom_1.wav', '../master/intercom_2.wav', '../master/intercom_3.wav']

if __name__ == '__main__':
    # masterの追加
    for filename in TARGET_FILES:
        print(filename, end=': ')
        wavefile = decoder.read(os.path.join(PATH, filename))
        if wavefile == None:
            print('cannot extract wav')
            continue

        with mysql_intercom.Database_intercom(CONFIG.DB_CONFIG) as db:
            master_id = db.insert_master(filename.split('/')[-1])
        if master_id > 0:
            print()
            print('sampling_rate =', wavefile.sampling_rate)
            target_hashes = fingerprint.fingerprint(wavefile.sounds) # hashの計算
            fingerprint.add_masters_hashes(master_id, target_hashes) # hashの追加
        else:
            print('cannot insert to masters')
            continue
