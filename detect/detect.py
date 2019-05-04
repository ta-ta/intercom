# coding: UTF-8

import logging
import numpy as np
import os
import sys

import detect_parameter as DETECT_PARAMETER
import env.local as CONFIG
import fingerprint
import log
import slack

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, '../db'))
import mysql_intercom

logger = logging.getLogger(CONFIG.LOG_INTERCOM)

def detect(now, wave_bytes) -> None:
    """ 判定 """
    wave = np.frombuffer(wave_bytes, dtype="int16") # -32768 ~ +32767
    target_hashes = list(fingerprint.fingerprint(wave))  # hashの計算
    matched_master = fingerprint.find_masters_hashes(target_hashes)  # DBから探すreturn_matches(hashes)
    detected_master = fingerprint.align_matches(matched_master)  # 時間差ごとにmaster_idをまとめる 最終結果を返す

    if detected_master != None:
        master_id = detected_master.master_id
        confidence = detected_master.confidence
        logger.info('master_id: %s, confidence: %s', master_id, confidence)

        # slack投稿
        message = now.strftime('%Y-%m-%d %H:%M:%S') + ' CONFIDENCE: ' + str(confidence)
        slack.post_slack(message, channel=CONFIG.CHANNEL)
