"""Alignment module."""

import numpy as np

from .img import IMG


def corr_offset(data, nav, axis):
    """Calculate the correlation offset of the navigation compare to the data.

    Parameters
    ----------
    data: numpy.array
        Input I/F data.
    nav: numpy.array
        Corresponding navigation data (inc/emi/phase/lat/lon/…).
    axis: int
        Axis to calculate the offset direction

    Returns
    -------
    int or (int, int)
        Navigation offset to match the I/F data.

    """
    if axis not in [0, 1]:
        raise ValueError('Axis must be `0` or `1.')

    _data = np.nansum(data, axis=axis)
    _nav = np.nansum(nav, axis=axis) > 0
    corr = np.correlate(_nav, _data, 'same')

    return len(corr) // 2 - np.argmax(corr)


def img_offset(arr, offset=False, is_data=True):
    """Offset image based on offset value.

    Parameters
    ----------
    arr: np.array:
        Data or navigation array.
    offset: bool or (int, int), optional
        Data offset compare to the navigation.
    is_data: bool, optional
        Apply offset on the I/F data if ``TRUE`` or
        on the navigation data if ``FALSE``.

    Returns
    -------
    ssi.IMG
        SSI image array.

    """
    if not offset:
        return IMG(arr)

    if is_data:
        return IMG(data_offset(arr, *offset))

    return IMG(nav_offset(arr, *offset))


def data_offset(data, ds, dl, fill_value=np.nan):
    """Data array with masked offset values."""
    mask = np.zeros(np.shape(data))

    if ds > 0:
        mask[:, :ds] = 1
    elif ds < 0:
        mask[:, ds:] = 1

    if dl > 0:
        mask[:dl, :] = 1
    elif dl < 0:
        mask[dl:, :] = 1

    return np.ma.array(data, mask=mask, fill_value=fill_value).filled()


def nav_offset(nav, ds, dl, fill_value=np.nan):
    """Navigation array with offsetted."""
    nl, ns = np.shape(nav)

    new = fill_value * np.ones((nl, ns))

    s0, s1, s2, s3 = (None, ns - ds, ds, None) if ds >= 0 else \
                     (-ds, None, None, ns + ds)

    l0, l1, l2, l3 = (None, nl - dl, dl, None) if dl >= 0 else \
                     (-dl, None, None, nl + dl)

    new[l2:l3, s2:s3] = nav[l0:l1, s0:s1]

    return new
