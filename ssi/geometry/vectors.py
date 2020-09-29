"""Vectors module."""

import numpy as np


def norm(v):
    """Vector norm.

    Parameters
    ----------
    v: np.array
        Input vector to measure(s).

    Returns
    -------
    float or np.array
        Input vector norm(s).

    Examples
    --------
    >>> norm([1, 0, 0])
    1
    >>> norm([1, 1, 1])
    1.732050...

    """
    return np.linalg.norm(v, axis=0)


def hat(v):
    """Normalize vector.

    Parameters
    ----------
    v: np.array
        Input vector to normalize.

    Returns
    -------
    np.array
        Normalize input vector.

    Examples
    ---------
    >>> hat([1, 0, 0])
    array([1., 0., 0.])
    >>> hat([1, 1, 1])
    array([0.577..., 0.577..., 0.577...])

    """
    return np.asarray(v) / norm(v)


def deg180(ang):
    """Restrict angle in [-180; 180[ degrees range.

    Parameters
    ----------
    ang: float
        Angle in degrees.

    Return
    ------
    float
        Angle mod 360° deg between -180° and 180°.

    Example
    -------
    >>> deg180(0)
    0
    >>> deg180(360)
    0
    >>> deg180(270)
    -90
    >>> deg180(-90)
    -90
    >>> deg180(-270)
    90

    """
    return (np.asarray(ang) + 180) % 360 - 180


def deg360(ang):
    """Restrict angle in [0; 360[ degrees range.

    Parameters
    ----------
    ang: float
        Angle in degrees.

    Return
    ------
    float
        Angle mod 360° deg between 0° and 360°.

    Example
    -------
    >>> deg360(0)
    0
    >>> deg360(360)
    0
    >>> deg360(-90)
    270
    >>> deg360(270)
    270
    >>> deg360(-270)
    90

    """
    return np.asarray(ang) % 360


def lonlat(xyz):
    """Convert cartesian coordinates into geographic coordinates.

    Parameters
    ----------
    xyz: numpy.array
        XYZ cartesian vector.

    Return
    ------
    (float, float)
        Longitude West (0 to 360) and Latitude North (deg).

    Examples
    --------
    >>> lonlat([1, 0, 0])
    (0, 0)
    >>> lonlat([0, 1, 0])
    (270, 0)
    >>> lonlat([1, 1, 0])
    (315, 0)
    >>> lonlat([1, 0, 1])
    (0, 45)

    """
    x, y, z = xyz
    lon_w = deg360(np.degrees(-np.arctan2(y, x)))
    lat = np.degrees(np.arcsin(z / norm(xyz)))
    return np.array([lon_w, lat])
