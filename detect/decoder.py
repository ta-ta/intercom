import soundfile as sf

class Wavefile():
    def __init__(self):
        self.sounds = None
        self.sampling_rate = None # サンプリング周波数

def get_wave_from_soundfile(filename) -> Wavefile:
    """ soundfileから取得 """
    wave = Wavefile()
    try:
        data, sampling_rate = sf.read(filename)
        wave.sounds = data # モノラルのみ対応
        wave.sampling_rate = sampling_rate
    except Exception as err:
        print(err)
        return None
    return wave

def read(filename) -> Wavefile:
    """ wavファイルから音源、サンプリング周波数 """
    wave = get_wave_from_soundfile(filename)
    return wave
