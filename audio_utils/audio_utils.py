import os
import warnings

from audioread.exceptions import NoBackendError
from IPython.display import display, Audio
import librosa
from matplotlib import pyplot as plt
import pandas as pd
from tqdm.notebook import tqdm

# def _create_audio_dataset(path, dataset_len, **kwargs):
#     if os.path.isdir(path):
#         file_count = 0
#         dataset_dict = {}
#         for file in os.listdir(path):

#         return {
#             path: [
#                 _create_audio_dataset(
#                     file,
#                     dataset_len=dataset_len - file_count,
#                     **kwargs
#                 ) for file in os.listdir(path)
#             ]
#         }
#     else:
#         datum_dict, _ = create_audio_datum(path, **kwargs)
#         return datum_dict, dataset_len - 1

# def _crawl_dir(path):
#     if os.path.isdir(path):
#         return {path: [_crawl_dir(file) for file in os.listdir(path)]}
#     else:
#         return path

class AudioDataset:
    @classmethod
    def from_file(path="./dataset.pkl"):
        return AudioDataset(pd.read_pickle(path))

    def __load_df_from_path(path):
        pass

    def __init__(self, path=None, df=None):
        if df:
            self.df = df
        elif path:
            self.df = self.__load_df_from_path(path)
        else:
            raise ValueError("Must supply path or dataframe")

    def export(self, name="dataset.pkl"):
        self.df.to_pickle(name)


def create_audio_datum(path: str, filename: str, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        audio_time, sr = librosa.load(os.path.expanduser(path), sr=None)
    audio_stft = librosa.stft(audio_time, **kwargs)
    return (sr, audio_time, audio_stft)


def create_audio_dataset(
    dataset_path: str, dataset_len=100, **kwargs
) -> pd.DataFrame:
    """ Creates audio dataset from file structure.

    Args:
        playlist_dir: Playlist directory path.
        # TODO dataset_len (optional): Number of audio files to include.

    Returns:
        df: Compiled dataframe representing this dataset.
    """

    # dir_dict = _crawl_dir(dataset_path)
    num_songs = 0
    song_names = []
    songs = []
    break_outer = False
    dir_iterator = tqdm(os.walk(dataset_path), leave=False)
    for root, dirs, files in dir_iterator:
        if break_outer:
            dir_iterator.close()
            break
        rel_root = root.replace(dataset_path, "", 1)
        for file in tqdm(files, leave=False):
            if num_songs >= dataset_len:
                break_outer = True
                continue
            song_name = file
            if rel_root != "":
                song_name = f"{rel_root}/{song_name}"
            song_names.append(song_name)
            try:
                songs.append(
                    create_audio_datum(f"{root}/{file}", file, **kwargs)
                )
            except NoBackendError:
                song_names.pop()
                continue
            num_songs += 1


    data = {
        "index": song_names,
        "columns": ["sampling_rate", "time_signal", "stft"],
        "data": songs,
        "index_names": ["songs"],
        "column_names": ["audio components"],
    }
    return pd.DataFrame.from_dict(data, orient="tight")

    # make into correct df?


    # for file in os.listdir(dataset_path):
    #     if os.path.isdir(file):
    #         _create_audio_dataset(
    #             file, dataset_len=dataset_len-file_count, **kwargs
    #         )
    #     else:
    #         create_audio_datum(file, **kwargs)
    #         file_count += 1

    # songs = os.listdir(playlist_dir)[:dataset_len]
    # if ".DS_Store" in songs:
    #     songs.remove(".DS_Store")
    # songs = [song for song in songs if ".json" not in song]

    # df_structure = dict(zip(songs, [None] * len(songs)))
    # for song_name in df_structure.keys():
    #     song_path = playlist_dir / song_name
    #     if os.path.isdir(song_path):
    #         components = os.listdir(song_path)
    #     else:
    #         components = [song_name]
    #     df_structure[song_name] = {}
    #     df_structure[song_name]["time_signals"] = dict(zip(components, [None] * len(components)))
    #     df_structure[song_name]["stfts"] = dict(zip(components, [None] * len(components)))
    #     df_structure[song_name]["sampling_rate"] = None
    # df = pd.DataFrame(df_structure)
    # for song_name, song_data in tqdm(df_structure.items()):
    #     sr = None
    #     song_path = playlist_dir / song_name
    #     for component in song_data["time_signals"]:
    #         if component == song_name:
    #             filepath = song_path
    #         else:
    #             filepath = song_path / component
    #         df[song_name]["time_signals"][component], sr_tmp = librosa.load(
    #             filepath, sr=None
    #         )
    #         # assumes all songs at same sampling rate
    #         assert(not sr or sr == sr_tmp)
    #         sr = sr_tmp
    #     df[song_name]["sampling_rate"] = sr

    # # calculate STFTs
    # for key in tqdm(songs):
    #     song = df[key]
    #     for component, data in tqdm(song["time_signals"].items(), leave=False):
    #         X = librosa.stft(data, **kwargs)
    #         song["stfts"][component] = X

    # return df

def display_song(song, display_stft=True):
    sr = song["sampling_rate"]
    for name, signal in song["time_signals"].items():
        signal = song["time_signals"][name]
        display_song_np(signal, sr)
        if display_stft:
            plt.figure()
            librosa.display.waveplot(signal, sr=sr)

def display_song_np(arr, fs):
    display(Audio(data=arr.reshape(-1), rate=fs))

def display_stft(stft, sr):
    stft_db = librosa.amplitude_to_db(stft)
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(stft_db, sr=sr, x_axis='time', y_axis='hz')
