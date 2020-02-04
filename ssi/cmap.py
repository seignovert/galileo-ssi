"""Custom Colormap."""

from matplotlib.colors import LinearSegmentedColormap, to_rgb


class CondColormap:
    """Conditional colormap.

    Parameters
    ----------
    name: str, optional
        The name of the colormap.

    Returns
    -------
    matplotlib.colors.LinearSegmentedColormap
        Unevenly distributed colormap.

    """

    def __new__(cls, color='tab:blue', name=None):
        return LinearSegmentedColormap.from_list(name, [
            (0, '#00000000'),
            (1, color),
        ])


class MaskColormap:
    """Masking colormap.

    Parameters
    ----------
    name: str, optional
        The name of the colormap.

    Returns
    -------
    matplotlib.colors.LinearSegmentedColormap
        Unevenly distributed colormap.

    """

    def __new__(cls, color='tab:red', alpha=.2, name=None):
        return LinearSegmentedColormap.from_list(name, [
            (0, (*to_rgb(color), alpha)),
            (1, '#00000000'),
        ])
