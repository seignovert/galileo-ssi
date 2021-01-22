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

    def __new__(cls, data, *args, **kwargs):  # pylint: disable=unused-argument
        return np.array(data).view(cls) if np.ndim(data) == 2 else \
            np.array(data).view(np.ndarray)

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, val):
        """Return data array based on value index."""
        if self.data.ndim == 1:
            return self._data[val]

        if isinstance(val, tuple) and len(val) == 2:
            if val[1] is None:
                return self._data[val]

            return self._data[_parse(val[1], self.NL), _parse(val[0], self.NS)]

        if isinstance(val, np.ndarray):
            return self._data[val]

        raise IndexError('Invalid format. Use:\n [INT|SLICE, INT|SLICE] with '
                         f'1 ≤ Sample ≤ {self.NS} and 1 ≤ Line ≤ {self.NL}')

    @property
    def shape(self):
        """Data shape."""
        return self.data.shape if self.data.ndim <= 1 else (self.NS, self.NL)

    @property
    def NS(self):
        """Sample width."""
        return self._data.shape[1]

    @property
    def NL(self):
        """Line height."""
        return self._data.shape[0]

    @property
    def _data(self):
        """Data content."""
        return np.array(self.data) if self.data.ndim > 1 else np.float32(self.data)
