"""Europa geological data module."""

from .cmap import UnitsColormap
from .data import DATA
from .units import GeolUnits


class EUROPA(metaclass=GeolUnits):
    """Europa geological map."""

    MAP = DATA / 'Europa_geol_map.png'

    LEGEND = {
        0: 'Unknown',
        25: 'Bands',
        50: 'Crater',
        75: 'Continuous crater ejecta',
        100: 'Discontinuous crater ejecta',
        125: 'Low albedo chaos',
        150: 'Knobby albedo chaos',
        175: 'Mottled albedo chaos',
        200: 'High albedo chaos',
        255: 'Ridged plains',
    }

    CMAP = UnitsColormap({
        0: '#9c9c9c',    # Unknown
        25: '#8400a8',   # Bands
        50: '#ffaa00',   # Crater
        75: '#ffd37f',   # Continuous crater ejecta
        100: '#ffebaf',  # Discontinuous crater ejecta
        125: '#267300',  # Low albedo chaos
        150: '#70a800',  # Knobby albedo chaos
        175: '#89cd66',  # Mottled albedo chaos
        200: '#d3ffbe',  # High albedo chaos
        255: '#bee8ff',  # Ridged plains
    }, name='europa_geol')
