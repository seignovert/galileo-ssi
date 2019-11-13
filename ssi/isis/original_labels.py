"""ISIS Original Labels module."""


class ISISOriginalLabels:
    """ISIS original labels object.

    Parameters
    ----------
    filename: str
        Isis cube filename.
    pvl: PVLObject
        PVL dict object.

    """

    def __init__(self, filename, pvl):
        self.filename = filename
        self.__pvl = pvl['OriginalLabel']
        self.__lbls = None

    def __repr__(self):
        return '\n'.join([
            f'<{self.__class__.__name__}> ',
            *self.lbls])

    def __iter__(self):
        return iter(self.lbls)

    @property
    def _start_byte(self):
        """Original label start byte."""
        return int(self.__pvl['StartByte']) - 1

    @property
    def _bytes(self):
        """Original label number of byte."""
        return int(self.__pvl['Bytes'])

    def _load(self):
        """Load original labels data."""
        with open(self.filename, 'rb') as f:
            f.seek(self._start_byte)
            data = f.read(self._bytes)
        return data.decode().splitlines()[1:-2]

    @property
    def lbls(self):
        """Collection of ISIS tables."""
        if self.__lbls is None:
            self.__lbls = self._load()
        return self.__lbls
