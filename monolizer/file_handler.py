import os
import shutil
from .monolizer import Monolizer

extensions = [".wav", ".wave"]
'''
Potential additions supported by PySoundFile library
{'AIFF': 'AIFF (Apple/SGI)',
 'AU': 'AU (Sun/NeXT)',
 'AVR': 'AVR (Audio Visual Research)',
 'CAF': 'CAF (Apple Core Audio File)',
 'FLAC': 'FLAC (FLAC Lossless Audio Codec)',
 'HTK': 'HTK (HMM Tool Kit)',
 'IRCAM': 'SF (Berkeley/IRCAM/CARL)',
 'MAT4': 'MAT4 (GNU Octave 2.0 / Matlab 4.2)',
 'MAT5': 'MAT5 (GNU Octave 2.1 / Matlab 5.0)',
 'MPC2K': 'MPC (Akai MPC 2k)',
 'NIST': 'WAV (NIST Sphere)',
 'OGG': 'OGG (OGG Container format)',
 'PAF': 'PAF (Ensoniq PARIS)',
 'PVF': 'PVF (Portable Voice Format)',
 'RAW': 'RAW (header-less)',
 'RF64': 'RF64 (RIFF 64)',
 'SD2': 'SD2 (Sound Designer II)',
 'SDS': 'SDS (Midi Sample Dump Standard)',
 'SVX': 'IFF (Amiga IFF/SVX8/SV16)',
 'VOC': 'VOC (Creative Labs)',
 'W64': 'W64 (SoundFoundry WAVE 64)',
 'WAV': 'WAV (Microsoft)',
 'WAVEX': 'WAVEX (Microsoft)',
 'WVE': 'WVE (Psion Series 3)',
 'XI': 'XI (FastTracker 2)'}
'''
class FileHandler():

    def __init__(self, folder=None, threshold=None):
        self._folder = None
        self.NULL_THRESHOLD=threshold
        if folder and os.path.exists(folder):
            self.folder = folder

    def __enter__(self):
        return self

    def __repr__(self):
        return '\n'.join(map(str, self.files))

    def __exit__(self, *args):
        self.close()

    def close(self):
        (f.close() for f in self.files)

    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, folder):
        self._folder = folder
        self.files = [Monolizer(os.path.join(folder, f),
                        threshold=self.NULL_THRESHOLD,
                        ) for f in self._list_audio_files(folder)]

    filenames = property(lambda self: [f.filename for f in self.files])

    empty_files = property(lambda self: [f for f in self.files if f.isEmpty])

    fake_stereo_files = property(lambda self: [f for f in self.files if f.isFakeStereo])

    def backup(self, folder='RAW', newfolder=True):
        def join(folder, inc=''):
            return os.path.join(self.folder, folder.rstrip('\\') + inc)

        dirname = join(folder)
        if newfolder:
            i = 1
            while os.path.exists(dirname):
                dirname = join(folder, str(i))
                i += 1
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        for filename in self.filenames:
            shutil.copyfile(filename, os.path.join(dirname, os.path.basename(filename)))

    def remove_empty_files(self):
        filenames = []
        for file in self.empty_files:
            filename = file.filename
            filenames.append(filename)
            file.remove()
            self.files.remove(file)
        return filenames

    def monolize_fake_stereo_files(self):
        filenames = []
        for file in self.fake_stereo_files:
            filename = file.filename
            filenames.append(filename)
            file.monolize()
        return filenames

    def _is_audio_file(self, file):
        _, file_extension = os.path.splitext(file)
        return file_extension.upper() in (name.upper() for name in extensions)

    def _list_audio_files(self, folder):
        return [f for f in os.listdir(folder) if self._is_audio_file(f)]

    def _list_audio_files_info(self, folder):
        files = []
        for file in self._list_audio_files(folder):
            with Monolizer(os.path.join(folder, file)) as f:
                files.append(str(f))
        return files
