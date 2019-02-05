import os
from .monolizer import Monolizer

extensions = [".wav", ".wave"]

class _FileInfo(Monolizer):

    def __init__(self, file=None):
        if file:
            self.file = file
            self.channel = self.chkMono()

    def isMono(self):
        return self.channel == 1 or self.channel == 0

    def toDelete(self):
        return self.channel == self.EMPTY

    def toMonolize(self):
        return self.isMono() and self.channels == 2


class FileHandler():
    file = None

    def __init__(self, file=None):
        if file and self._isAudioFile(file):
            self.file = file

    def _isAudioFile(self, file):
        _, file_extension = os.path.splitext(file)
        return file_extension.upper() in (name.upper() for name in extensions)
