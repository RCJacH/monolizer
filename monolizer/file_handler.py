from .monolizer import Monolizer

class _FileInfo(Monolizer):
    toDelete = False
    toMonolize = False

    def __init__(self, file=None):
        if file:
            self.file = file
            self.channel = self.monolize()

    def isMono(self):
        return self.channel == 1 or self.channel == 0

    def toDelete(self):
        return self.channel == self.EMPTY

    def toMonolize(self):
        return self.isMono() and self.channels == 2
