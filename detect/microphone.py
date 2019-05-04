# coding: UTF-8

import logging
import sys
import wave

import pyaudio

import detect_parameter as DETECT_PARAMETER
import env.local as CONFIG
import log

logger = logging.getLogger(CONFIG.LOG_INTERCOM)

def set_device_index():
    DETECT_PARAMETER.DeviceIndex = -1
    iAudio = pyaudio.PyAudio()
    for i in range(iAudio.get_device_count()):
        if DETECT_PARAMETER.MICROPHONE == iAudio.get_device_info_by_index(i)['name']:
            DETECT_PARAMETER.DeviceIndex = i
            break
    else:
        logger.warning('cannot connect microphone: %s', DETECT_PARAMETER.MICROPHONE) # マイクとの接続不可
    logger.info('DeviceIndex: %d', DETECT_PARAMETER.DeviceIndex)

def get_wave():
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=DETECT_PARAMETER.FORMAT, channels=DETECT_PARAMETER.CHANNELS,
            rate=DETECT_PARAMETER.SAMPLING_FREQUENCY, input=True,
            input_device_index = DETECT_PARAMETER.DeviceIndex,
            frames_per_buffer=DETECT_PARAMETER.CHUNKS)
    except OSError as err:
        logger.exception(err)
        sys.exit()

    # 録音
    wave_buffers = []
    for i in range(int(DETECT_PARAMETER.SAMPLING_FREQUENCY / DETECT_PARAMETER.CHUNKS * DETECT_PARAMETER.RECORD_SECONDS)):
        wave_buffer = stream.read(DETECT_PARAMETER.CHUNKS)
        wave_buffers.append(wave_buffer)
    wave_bytes = b''.join(wave_buffers)

    # 録音終了
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return wave_bytes

def get_wave_stream():
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=DETECT_PARAMETER.FORMAT, channels=DETECT_PARAMETER.CHANNELS,
            rate=DETECT_PARAMETER.SAMPLING_FREQUENCY, input=True,
            input_device_index = DETECT_PARAMETER.DeviceIndex,
            frames_per_buffer=DETECT_PARAMETER.CHUNKS)
    except OSError as err:
        logger.exception(err)
        sys.exit()

    # 録音
    while True:
        wave_buffers = []
        for i in range(int(DETECT_PARAMETER.SAMPLING_FREQUENCY / DETECT_PARAMETER.CHUNKS * DETECT_PARAMETER.RECORD_SECONDS)):
            # if stream.is_active(): ### todo
            wave_buffer = stream.read(DETECT_PARAMETER.CHUNKS)
            wave_buffers.append(wave_buffer)
            #else:
            #   yield b''.join(wave_buffers)
            # wave_buffers = []
        wave_bytes = b''.join(wave_buffers)
        yield wave_bytes

    # 録音終了
    stream.stop_stream()
    stream.close()
    audio.terminate()

def output_file(wave_bytes, filename='output.wav'):
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(DETECT_PARAMETER.CHANNELS)
    waveFile.setsampwidth(pyaudio.PyAudio().get_sample_size(DETECT_PARAMETER.FORMAT))
    waveFile.setframerate(DETECT_PARAMETER.SAMPLING_FREQUENCY)
    waveFile.writeframes(wave_bytes)
    waveFile.close()
