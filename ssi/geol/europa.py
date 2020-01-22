"""Europa geological data module."""

from .data import DATA
from .units import GeolUnits

from matplotlib.colors import ListedColormap


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
        175: 'Molted albedo chaos',
        200: 'High albedo chaos',
        255: 'Ridged plains',
    }

    CMAP = ListedColormap([
        '#8400a8',
        '#ffaa00',
        '#ffd37f',
        '#ffebaf',
        '#267300',
        '#70a800',
        '#89cd66',
        '#d3ffbe',
        '#bee8ff',
    ])
