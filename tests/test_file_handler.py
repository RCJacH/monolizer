import pytest
import os
import shutil
from monolizer import FileHandler, Monolizer
from soundfile import read

all_files = set(['empty.wav', 'sin.wav', 'sins.wav', 'sin_l50.wav',
                'sin_r25.wav', 'sin_r100.wav', 'sin_tri.wav', 'sinwave.wave'])
fake_stereo_files = set(['sins.wav', 'sin_l50.wav', 'sin_r25.wav', 'sin_r100.wav'])

def get_file_set(filelist):
    return set(os.path.basename(f.filename) for f in filelist)

@pytest.fixture(scope='function')
def tmpdir():
    tmpdir = 'tests\\tmpdir'
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    yield tmpdir
    shutil.rmtree(tmpdir)

class Test_FileHandler(object):

    def test__init__no_input(self):
        obj = FileHandler()
        assert obj.folder == None

    def test__init__file(self):
        obj = FileHandler('tests')
        assert obj.folder == 'tests'

    def test_is_audio_file(self):
        obj = FileHandler()
        assert obj._is_audio_file('tests.wav')
        assert obj._is_audio_file('tests.Wav')
        assert obj._is_audio_file('tests.WAV')
        assert obj._is_audio_file('tests.WAVE')
        assert not obj._is_audio_file('tests.txt')

    def test_list_audio_files(self):
        obj = FileHandler()
        assert (set(obj._list_audio_files('tests')) == all_files)

    def test_empty_files(self):
        with FileHandler('tests') as folder:
            assert get_file_set(folder.empty_files) == set(['sinwave.wave', 'empty.wav'])

    def test_fake_stereo_files(self):
        with FileHandler('tests') as folder:
            assert get_file_set(folder.fake_stereo_files) == fake_stereo_files

    def test_backup(self):
        base = 'tests'
        default = os.path.join(base, 'RAW')
        default_inc = os.path.join(base, 'RAW1')
        with FileHandler(base) as folder:
            folder.backup()
            assert set(os.path.basename(f) for f in os.listdir(default)) == all_files
            assert os.path.exists(default)
            os.remove(os.path.join(default, 'sin.wav'))
            assert set(os.path.basename(f) for f in os.listdir(default)) != all_files

            folder.backup(newfolder=False)
            assert os.path.exists(default)
            assert set(os.path.basename(f) for f in os.listdir(default)) == all_files

            folder.backup(newfolder=True)
            assert os.path.exists(default_inc)
            assert set(os.path.basename(f) for f in os.listdir(default_inc)) == all_files
        shutil.rmtree(default)
        shutil.rmtree(default_inc)

    def test_delete_empty_files(self, tmpdir):
        tmp_empty = os.path.join(tmpdir, 'empty.wav')
        tmp_sin = os.path.join(tmpdir, 'sin.wav')
        shutil.copyfile('tests\\empty.wav', tmp_empty)
        shutil.copyfile('tests\\sin.wav', tmp_sin)
        with FileHandler(tmpdir) as folder:
            folder.delete_empty_files()
            assert 'empty.wav' not in folder.filenames
        assert os.listdir(tmpdir) == ['sin.wav']

    def test_monolize_fake_stereo_files(self, tmpdir):
        obj = FileHandler()
        for file in obj._list_audio_files('tests'):
            shutil.copyfile(os.path.join('tests', file), os.path.join(tmpdir, file))
        with FileHandler(tmpdir) as folder:
            folder.monolize_fake_stereo_files()
            assert all([f.channels == 1 for f in folder.fake_stereo_files])
