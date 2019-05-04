# coding: UTF-8

import datetime
import logging
import os
import queue
import sys
import threading
import time

import decoder
import detect
import detect_parameter as DETECT_PARAMETER
import env.local as CONFIG
import log
import microphone

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, '../db'))
import mysql_intercom

logger = logging.getLogger(CONFIG.LOG_INTERCOM)

# DB テーブル作っておく
with mysql_intercom.Database_intercom(
        CONFIG.DB_CONFIG) as db:
    db.create_masters_table()
    db.create_fingerprints_table()

# queue
WAVE_QUEUE = queue.Queue(maxsize=20)
def enqueue_wave():
    wave_bytes_gen = microphone.get_wave_stream()
    while True:
        now = datetime.datetime.now()
        try:
            wave_bytes = next(wave_bytes_gen)
            WAVE_QUEUE.put([now, wave_bytes], block=True, timeout=DETECT_PARAMETER.RECORD_SECONDS)
        except queue.Full as err:
            logger.exception(err)

def dequeue_wave():
    time.sleep(DETECT_PARAMETER.RECORD_SECONDS)
    while True:
        try:
            now, wave_bytes = WAVE_QUEUE.get(block=True, timeout=DETECT_PARAMETER.RECORD_SECONDS)
            detect.detect(now, wave_bytes)
        except queue.Empty as err:
            logger.warning('cannot get microphone input')
            logger.exception(err)
            break

if __name__ == '__main__':
    logger.info('started')

    microphone.set_device_index()

    enqueue_wave_thread = threading.Thread(target=enqueue_wave)
    enqueue_wave_thread.setDaemon(True)
    dequeue_wave_thread = threading.Thread(target=dequeue_wave)

    enqueue_wave_thread.start()
    dequeue_wave_thread.start()

    # マイクとの接続が切れた時は勝手に終了するが、明示的に書いておく
    dequeue_wave_thread.join()
    sys.exit()
