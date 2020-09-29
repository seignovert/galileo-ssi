"""Geological units module."""

import matplotlib.pyplot as plt

import numpy as np


def grid(img, lon_w, lat):
    """Convert geographic coordinates as image coordinates.

    Parameters
    ----------
    img: 2d-array
        2D geol map image centered at 180°.
    lon_w: float or array
        Point west longitude(s).
    lat: float or array
        Point latitude(s).

    Returns
    -------
    int or array, int or array
        Array closest coordinates on the image.

    """
    h, w = np.shape(img)

    if isinstance(lon_w, (list, tuple)):
        lon_w = np.array(lon_w)

    if isinstance(lat, (list, tuple)):
        lat = np.array(lat)

    i = np.round(-lon_w % 360 * w / 360).astype(int)
    j = np.round((90 - lat) * h / 180).astype(int)

    if isinstance(lon_w, (int, float)):
        if i >= w or np.isnan(lon_w):
            i = w - 1
        if np.isnan(lat):
            j = h - 1
    else:
        i[(i >= w) | np.isnan(lon_w)] = w - 1
        j[np.isnan(lat)] = h - 1

    return i, j


def geol_units(img, lon_w, lat, legend=None):
    """Get geological units based on (lon, lat) coordinates.

    Parameters
    ----------
    img: 2d-array
        2D geol map image centered at 180°.
    lon_w: float or array
        Point west longitude(s).
    lat: float or array
        Point latitude(s).
    legend: dict, optional
        Table to mapping geol units to values.

    Returns
    -------
    float, str or array
        Geological unit(s).

    """
    i, j = grid(img, lon_w, lat)
    units = img[j, i]

    if not isinstance(legend, dict):
        if np.ma.is_masked(lon_w) or np.ma.is_masked(lat):
            mask = np.ma.getmask(lon_w) | np.ma.getmask(lat)
            return np.ma.array(units, mask=mask)
        return units

    if np.ndim(units) == 0:
        return legend[units]

    geol = np.vectorize(legend.get)(units)

    if np.ma.is_masked(lon_w) or np.ma.is_masked(lat):
        mask = np.ma.getmask(lon_w) | np.ma.getmask(lat)
        return np.ma.array(geol, mask=mask)

    return geol


def _key(data, value):
    """Get key in data from value.

    Note
    ----
    Only the first iteration

    """
    if not isinstance(data, dict):
        raise TypeError('Data must be a dict')

    return [k for k, v in data.items() if value == v]


class GeolUnits(type):
    """Geological map units."""

    MAP = None
    LEGEND = None
    IMG = None

    EXTENT = [360, 0, -90, 90]  # Map extent

    def __str__(cls):
        return cls.__name__

    def __repr__(cls):
        return '\n - '.join([
            f'<{cls.__class__.__name__}> {cls} | Units:',
            *cls.LEGEND.values()
        ])

    def __call__(cls, *args, legend=True):
        """Get geological units form image."""
        if len(args) == 1:
            img = args[0]

            if not hasattr(img, 'lon'):
                raise AttributeError('Missing `lon` attribute in image.')

            if not hasattr(img, 'lat'):
                raise AttributeError('Missing `lat` attribute in image.')

            lon_w = np.ma.array(img.lon, mask=img.limb)
            lat = np.ma.array(img.lat, mask=img.limb)
            return cls.geol_units(lon_w, lat, legend=legend)  # pylint: disable=E1120

        if len(args) == 2:
            lon, lat = args
            return cls.geol_units(lon, lat, legend=legend)  # pylint: disable=E1120

        raise TypeError('Takes anf IMAGE or LON and LAT value(s).')

    def __iter__(cls):
        return iter(cls.LEGEND.items())

    @property
    def img(cls):
        """Map image data."""
        if cls.IMG is None:
            cls.IMG = (plt.imread(str(cls.MAP)) * 255).astype(np.uint8)
        return cls.IMG

    def geol_units(cls, lon_w, lat, legend=True):
        """Get geological units.

        Parameters
        ----------
        lon_w: float or array
            Point west longitude(s).
        lat: float or array
            Point latitude(s).
        legend: dict, optional
            Table to mapping geol units to values.
            By default, the values are legend based
            on the map geological legend.

        Returns
        -------
        float, str or array
            Geological unit(s) or value(s) (if `legend` is set to `False`).

        """
        if legend and isinstance(legend, bool):
            legend = cls.LEGEND

        return geol_units(cls.img, lon_w, lat, legend=legend)

    def color(cls, unit, cmap=None, legend=None):
        """Get color from unit name."""
        if cmap is None:
            cmap = cls.CMAP

        if legend is None:
            legend = cls.LEGEND

        colors = [cmap(k) for k in _key(legend, unit)]

        if not colors:
            raise ValueError(f'Unit unknown: `{unit}`.')

        return colors[0] if len(colors) == 1 else colors
