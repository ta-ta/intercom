# coding: UTF-8

import os
import sys
from itertools import zip_longest
from typing import List, NewType, Tuple

import cv2
import matplotlib.mlab as mlab
import numpy as np
import xxhash
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure)

import detect_parameter as DETECT_PARAMETER
import env.local as CONFIG

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PATH, '../db'))
import mysql_intercom

PEAK_INDEX = NewType('PEAK_INDEX', Tuple[List[int], List[int]])

Time_idx = 0
Frequency_idx = 1


class Detected():
    def __init__(self, master_id=None, confidence=None):
        self.master_id = master_id  # 判定結果のmaster_id
        self.confidence = confidence  # 判定結果でのマッチしたハッシュの数

    def __lt__(self, detect_music):
        return self.confidence < detect_music.confidence

def fingerprint(wave):
    """ 対数振幅スペクトログラムを計算する。local_peakを求めて、そのハッシュを返す """
    if len(wave) < DETECT_PARAMETER.WINDOW_SIZE: # 十分な長さの音声信号がない時
        return (None, None)
    # FFT (パワースペクトル)
    spectrogram, _, _ = mlab.specgram(
        wave,
        NFFT=DETECT_PARAMETER.WINDOW_SIZE,
        Fs=DETECT_PARAMETER.SAMPLING_FREQUENCY,
        window=np.hamming(DETECT_PARAMETER.WINDOW_SIZE),
        noverlap=int(DETECT_PARAMETER.WINDOW_SIZE * DETECT_PARAMETER.OVERLAP_RATIO))

    # log amplitude
    with np.errstate(divide='ignore'):
        spectrogram = 10 * np.log10(spectrogram)
    spectrogram[spectrogram == -np.inf] = 0.0  # replace infs with zeros
    # find local maxima
    frequency_idx, time_idx = get_local_peaks_index(spectrogram)  # ピーク探す

    # ハッシュを返す
    return generate_hashes(frequency_idx, time_idx)


def get_local_peaks_index(spectrogram) -> PEAK_INDEX:
    """ local peak を探し、インデックスのペアを返す """
    # スペクトログラムのピークを見つけて、インデックスのペアを返す
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, DETECT_PARAMETER.PEAK_NEIGHBORHOOD_SIZE)

    # スペクトログラムの各要素に対して、今見ている範囲内の最大値を返す。その最大値と元の要素が等しければTrue
    local_max = (cv2.dilate(spectrogram, neighborhood.astype(np.uint8)) == spectrogram)

    # 一定以上の振幅があり、局所的に最大ならTrue
    detected_peaks = np.where(spectrogram > DETECT_PARAMETER.MIN_AMPLITUDE, local_max, False)

    # extract peaks
    frequency_idx, time_idx = np.where(detected_peaks) # time_idxでソート済み

    return frequency_idx, time_idx


def generate_hashes(frequency_idx, time_idx):
    """ ピークのインデックスを使ってハッシュを計算する """
    # 次のピークとのハッシュを返す
    # 時間差の条件あり

    time_frequency = []
    for f_idx, t_idx in zip(frequency_idx, time_idx):
        time_frequency.append([t_idx, f_idx])
    # 時間順、周波数順にする
    time_frequency.sort()

    peak_len = len(time_frequency)
    for i in range(peak_len):
        for j in range(1, DETECT_PARAMETER.FAN_VALUE):
            if (i + j) < peak_len:
                freq1 = time_frequency[i][Frequency_idx]
                freq2 = time_frequency[i + j][Frequency_idx]
                t1 = time_frequency[i][Time_idx]
                t2 = time_frequency[i + j][Time_idx]
                time_delta = t2 - t1

                if time_delta <= DETECT_PARAMETER.MAX_HASH_TIME_DELTA:
                    h = xxhash.xxh32("%s|%s|%s" % (str(freq1), str(freq2), str(time_delta)))
                    yield (h.hexdigest(), t1)


def find_masters_hashes(target_hashes):
    """ ハッシュを受け取り、それをfingerprintsから探す。master_idと時間差を返す """
    mapper = {}
    for hash, offset in target_hashes:
        # 一つの動画内に同じハッシュがあったときは、最初の方を採用
        if mapper.get(hash.upper(), None) == None:
            mapper[hash.upper()] = offset

    values = mapper.keys()
    for split_values in grouper(values, 1000): # 1000ずつクエリ
        with mysql_intercom.Database_intercom(CONFIG.DB_CONFIG) as db:
            fingerprints = db.fetch_master_id_by_hashes(list(split_values))
        for hash, master_id, offset in fingerprints:
            yield (master_id, offset - mapper[hash])

def grouper(iterable, N, fillvalue=None):
    """ Nずつグループ化する """
    args = [iter(iterable)] * N
    return (filter(None, values) for values in zip_longest(fillvalue=fillvalue, *args))


def align_matches(matched_master) -> Detected:
    """ マッチしたハッシュ同士の時間差が最も多かったものを判定結果としてを返す """
    # master_idとその時間差から
    # 時間差ごとにmasterの数を数える
    diff_counter = {}
    max_confidence = 0
    master_id = 0
    difference = 0
    for m_id, diff in matched_master:
        if diff not in diff_counter:
            diff_counter[diff] = {}
        if m_id not in diff_counter[diff]:
            diff_counter[diff][m_id] = 0
        diff_counter[diff][m_id] += 1
        if diff_counter[diff][m_id] > max_confidence:
            max_confidence = diff_counter[diff][m_id]
            master_id = m_id
            difference = diff
    if max_confidence <= DETECT_PARAMETER.MIN_CONFIDENCE:
        return None
    return Detected(master_id=master_id, confidence=max_confidence)


def add_masters_hashes(master_id, target_hashes):
    """ ハッシュを受け取り、それをfingerprintsに入れる """
    hashes = set()
    for hash, offset in target_hashes:
        hashes.add((hash.upper(), offset))
    for split_values in grouper(hashes, 1000):  # 1000ずつクエリ
        with mysql_intercom.Database_intercom(CONFIG.DB_CONFIG) as db:
            db.insert_fingerprints(master_id, list(split_values))
