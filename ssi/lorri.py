"""New Horizons LORRI camera."""

import re

import numpy as np

from .ssi import SSI


AU = 1.49598e8         # 1 AU in km
F_SOLAR = 176 * AU**2  # erg/cm2/s/Å/km^2


def _fits_hdr(lines):
    """Parse ISIS fits original header."""
    hdr = {}
    for line in lines:
        key, value = _parse(line.strip())

        if key is None:
            continue

        if key in hdr.keys():
            raise ValueError(f'Key: `{key}` is already defined in FITS header.')

        hdr[key] = value

    return hdr


def _parse(line):
    """Parse ISIS fits original header line."""
    if line.startswith('#') or line.startswith('COMMENT') or ' = ' not in line:
        return None, None

    key, values = line.split(' = ', 1)

    return key.strip(), _values(values.strip())


def _values(values):
    """Parse values."""
    floats = re.findall(r'-?\d+\.\d*(?:[eE]?[-+]?\d+)', values)
    if floats:
        values = [float(v) for v in floats]
    else:
        ints = re.findall(r'^(-?\d+)\s?(?![\w\-/:\.])', values)
        if ints:
            values = [int(i) for i in ints]
        else:
            values = values.replace('"', '')

    return values if len(values) > 1 else values[0]


class LORRI(SSI):
    """New Horizons LORRI camera.

    Extent Galileo SSI camera model.

    Parameters
    ----------
    filename: str
        Input SSI filename.
    src: str, optional
        Spectral distribution src (see fits header).
    align: bool, optional
        Enable data auto-alignment.
    offset_s: int, optional
        Provide sample offset to apply to the data.
    offset_l: int, optional
        Provide line offset to apply to the data.

    """

    def __init__(self, *args, src='RSOLAR', **kwargs):
        self.src = src
        self.__fits = None

        super().__init__(*args, **kwargs)

    @property
    def src(self):
        """Spectral distribution source."""
        return self.__src

    @src.setter
    def src(self, src):
        self.__src = src
        self.__data = None

    @property
    def start(self):
        """Instrument start time (UTC)."""
        return self._inst['StartTime'].value

    @property
    def stop(self):
        """Instrument stop time (UTC)."""
        return None

    @property
    def filter_name(self):
        """Filter name."""
        return 'None'

    @property
    def exposure(self):
        """ISIS header exposure duration."""
        return (self._inst['ExposureDuration'], 'sec')

    @property
    def fits_hdr(self):
        """Original fits header."""
        if self.__fits is None:
            self.__fits = _fits_hdr(self.original_labels)
        return self.__fits

    @property
    def _radiance(self):
        """Radiance convertion factor based on ``src`` attribute."""
        return self.fits_hdr[self.src]

    @property
    def sun_dist(self):
        """Sun range to Target center (km)."""
        return self.fits_hdr['SPCTSORN']

    @property
    def _f(self):
        """Solar flux at target distance (erg/cm^2/s/Å)."""
        return F_SOLAR / np.pi / self.sun_dist ** 2

    @property
    def _i(self):
        """Image Radiance value (erg/cm^2/s/sr/Å)."""
        return self['Data'] / self.exposure[0] / self._radiance

    @property
    def data(self):
        """Image I/F data.

        Note
        ----
        The radiance calibration is based on the LORRI
        instrument pipeline instruction
        (`soc_inst_icd_lorri.pdf` v0.0 p.40).

        The spectral radiance distribution is based
        on the ``src`` attribute. See fits header to change

        """
        if self.__data is None:
            self.__data = self._i / self._f
        return self.__data
