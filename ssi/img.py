"""Image module."""

import numpy as np


def _parse(index, n):
    """Parse index value(s).

    Images must be between ``1`` and ``n``.

    Parameters
    ----------
    index: int or slice
        Index to parse.
    n: int
        Image max size (width or height).
    name: str
        Name of the dimension

    """
    if index is None:
        return None

    if isinstance(index, int):

        if index < 1:
            raise IndexError(f'Index `{index}` must be > 1.')

        if index > n:
            raise IndexError(f'Index `{index}` must be < {n}.')

        return index - 1

    if isinstance(index, slice):
        return slice(_parse(index.start, n), _parse(index.stop, n), index.step)

    raise IndexError(f'Unsupported type `{type(index)}`. Index must be `int` or `slice`.')


class IMG(np.ndarray):
    """Image object based on Numpy array."""
    def __new__(cls, data):
        obj = np.asarray(data).view(cls)
        cls.__data = np.asarray(data)
        return obj

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        return repr(self.__data)

    def __getitem__(self, val):
        """Return data array based on value index."""
        if isinstance(val, tuple) and len(val) == 2:
            return self.__data[_parse(val[1], self.NL), _parse(val[0], self.NS)]

        if isinstance(val, np.ndarray):
            return self.__data[val]

        raise IndexError('Invalid format. Use:\n [INT|SLICE, INT|SLICE] with '
            f'1 ≤ Sample ≤ {self.NS} and 1 ≤ Line ≤ {self.NL}')

    @property
    def NL(self):
        """Sample width."""
        return self.shape[1]

    @property
    def NS(self):
        """Line height."""
        return self.shape[0]
