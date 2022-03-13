import os
import urllib.request

import librosa
import pd
from tqdm import tqdm

MUSDB18_URL = "https://zenodo.org/record/1117372/files/musdb18.zip?download=1"
MUSDB18HQ_URL = "https://zenodo.org/record/3338373/files/musdb18hq.zip?download=1"


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def _download_dataset_from_url(url):
    with urllib.request.urlopen(url) as response:
        headers = response.getheaders()
        content_disposition = next(
            header for header in headers if header[0] == "Content-Disposition"
        )[1]
        if "attachment" not in content_disposition:
            raise ValueError("Expecting download attachment.")
        default_filename = content_disposition.split(' ')[1].split("=")[1]


    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=default_filename, reporthook=t.update_to)

    return default_filename


def _load_dataset_into_memory(dataset_path):
    songs = os.listdir(dataset_path)[:2]
    if ".DS_Store" in songs: songs.remove(".DS_Store")

    df_structure = dict(zip(songs, [None] * len(songs)))
    for song_name in df_structure.keys():
        song_dir = dataset_path / song_name
        components = os.listdir(song_dir)
        df_structure[song_name] = {}
        df_structure[song_name]["time_signals"] = dict(zip(components, [None] * len(components)))
        df_structure[song_name]["stfts"] = dict(zip(components, [None] * len(components)))
        df_structure[song_name]["sampling_rate"] = None
    df = pd.DataFrame(df_structure)
    for song_name, song_data in tqdm(df_structure.items()):
        sr = None
        song_dir = dataset_path / song_name
        for component in song_data["time_signals"]:
            df[song_name]["time_signals"][component], sr_tmp = librosa.load(
                song_dir / component, sr=None
            )
            # assumes all songs at same sampling rate
            assert(not sr or sr == sr_tmp)
            sr = sr_tmp
        df[song_name]["sampling_rate"] = sr

    return musdb18


def musdb18():
    file = _download_dataset_from_url(MUSDB18_URL)

    # TODO figure out test as well
    return _load_dataset_into_memory(file / "train")


def musdb18hq():
    file = _download_dataset_from_url(MUSDB18HQ_URL)

    return _load_dataset_into_memory(file)
