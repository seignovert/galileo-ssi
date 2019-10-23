"""Alignment module."""

import numpy as np


def offset(data, nav, axis=-1):
    """Calculate the offset between the data and navigation.

    Parameters
    ----------
    data: numpy.array
        Input I/F data.
    nav: numpy.array
        Corresponding navigation data (inc/emi/phase/lat/lon/…).
    axis: int, optional
        Axis to calculate the offset direction:
            * ``-1``: both axis.

    Returns
    -------
    int or (int, int)
        Data offset to match the navigation.

    """
    if axis == -1:
        return offset(data, nav, axis=0), offset(data, nav, axis=1)

    if axis not in [0, 1]:
        raise ValueError('Axis must be `0` or `1.')

    _data = np.nansum(data, axis=axis)
    _nav = np.nansum(nav, axis=axis) > 0
    cross = np.correlate(_data, _nav, 'same')

    return len(cross) // 2 - np.argmax(cross)
