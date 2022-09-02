"""Pluto geological data module."""

from .cmap import UnitsColormap
from .data import DATA
from .units import GeolUnits


class PLUTO(metaclass=GeolUnits):
    """Pluto geological map."""

    MAP = DATA / 'Pluto_geol_map.png'

    LEGEND = {
        0: 'No data',
        64: 'Washboard units',
        127: 'Sputnik Planitia',
        255: 'Bladed units',
    }

    CMAP = UnitsColormap({
        0: '#00000000',  # No-data
        64: '#00ff00',   # Washboard units
        127: '#0000ff',  # Sputnik Planitia
        255: '#ff0000',  # Bladed unit
    }, name='pluto_geol')
