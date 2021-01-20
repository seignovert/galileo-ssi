"""VIMS ISIS header."""

import os

import numpy as np

import pvl

from .dtime import dtime
from .errors import ISISError
from .labels import ISISLabels
from .original_labels import ISISOriginalLabels
from .tables import ISISTables
from .vars import BYTE_ORDERS, FIELD_TYPES
from ..geometry import hat, lonlat, q_rot


class ISISCube:
    """VIMS ISIS header object.

    Parameters
    ----------
    filename: str
        Input ISIS filename.

    """

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return self.filename

    def __repr__(self):
        return f'<{self.__class__.__name__}> ISIS Cube: {self}'

    def __contains__(self, key):
        return key in self.keys()

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(f'Key `{key}` not found.')

        if key in self.labels:
            return self.labels[key]

        return self.tables[key]

    @property
    def filename(self):
        """Filename."""
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__filename = filename
        self.__pvl = None
        self.__labels = None
        self.__tables = None
        self.__lbls = None
        self.__cube = None

        if not self.is_file:
            raise FileNotFoundError(f'File `{self.filename}` not found.')

        if not self.is_isis:
            raise ISISError(f'File `{self.filename}` is not in ISIS format.')

    @property
    def is_file(self):
        """Check if the file exists."""
        return os.path.exists(self.filename)

    @property
    def is_isis(self):
        """Check if the file is in ISIS format."""
        with open(self.filename, 'rb') as f:
            header = f.read(17)

        return header == b'Object = IsisCube'

    @property
    def pvl(self):
        """Full ISIS header in PVL format."""
        if self.__pvl is None:
            self.__pvl = pvl.load(self.filename)
        return self.__pvl

    @property
    def labels(self):
        """ISIS label labels."""
        if self.__labels is None:
            self.__labels = ISISLabels(self.pvl)
        return self.__labels

    @property
    def tables(self):
        """ISIS tables."""
        if self.__tables is None:
            self.__tables = ISISTables(self.filename, self.pvl)
        return self.__tables

    def keys(self):
        """ISIS labels and tables keys."""
        return list(self.labels.keys()) + list(self.tables.keys())

    @property
    def header(self):
        """Main ISIS Cube header."""
        return self.pvl['IsisCube']

    @property
    def _core(self):
        """ISIS core header."""
        return self.header['Core']

    @property
    def _dim(self):
        """ISIS dimension header."""
        return self._core['Dimensions']

    @property
    def NS(self):
        """Number of samples."""
        return self._dim['Samples']

    @property
    def NL(self):
        """Number of lines."""
        return self._dim['Lines']

    @property
    def NB(self):
        """Number of bands."""
        return self._dim['Bands']

    @property
    def shape(self):
        """Cube shape."""
        return (self.NB, self.NL, self.NS)

    @property
    def _pix(self):
        """ISIS core header."""
        return self._core['Pixels']

    @property
    def dtype(self):
        """Cube data type."""
        return np.dtype(
            BYTE_ORDERS[self._pix['ByteOrder']]  # noqa: W504
            + FIELD_TYPES[self._pix['Type']])   # noqa: W503

    @property
    def _start_byte(self):
        """Cube data start byte."""
        return self._core['StartByte'] - 1

    @property
    def _nbytes(self):
        """Cube data bytes size."""
        return self.NB * self.NL * self.NS * self.dtype.itemsize

    @property
    def _base(self):
        """Cube data base factor."""
        return self._pix['Base']

    @property
    def _mult(self):
        """Cube data multiplication factor."""
        return self._pix['Multiplier']

    @property
    def cube(self):
        """ISIS cube."""
        if self.__cube is None:
            self.__cube = self._load_data()
        return self.__cube

    def _load_data(self):
        """Load ISIS table data."""
        with open(self.filename, 'rb') as f:
            f.seek(self._start_byte)
            data = f.read(self._nbytes)

        data = np.frombuffer(data, dtype=self.dtype) * self._mult + self._base

        if self.dtype.char == 'f':
            # Fix saturated pixel (stored as underflow)
            dmax = np.max(data)
            data[data == self._underflow] = dmax

            data[self._is_null(data)] = np.nan

        return self._reshape(data)

    @property
    def _underflow(self):
        """Data type underflow value."""
        return np.finfo(self.dtype).min if self.dtype.char == 'f' \
            else np.iinfo(self.dtype).min

    @property
    def _overflow(self):
        """Data type overflow value."""
        return np.finfo(self.dtype).max if self.dtype.char == 'f' \
            else np.iinfo(self.dtype).max

    def _is_null(self, data, tol=1e-6):
        """Find NULL values.

        Find the values lower than underflow or higher than overflow.

        Parameters
        ----------
        data: np.array
            Input array to test.
        tol: float
            Relative tolerance factor

        Returns
        -------
        np.array
            Location of the null values.

        """
        if self.dtype.char != 'f':
            return False

        return (np.abs(data / self._underflow) >= tol) | \
            (np.abs(data / self._overflow) >= tol)

    @property
    def _TL(self):
        """Number of tiles in the line direction."""
        return self._core['TileLines']

    @property
    def _TS(self):
        """Number of tiles in the sample direction."""
        return self._core['TileSamples']

    def _reshape(self, data):
        """Reshape data based on tile size."""
        if self._TS == self.NS and self._TL == self.NL:
            return np.reshape(data, self.shape)

        size = np.size(data)
        shape = (size // (self._TL * self._TS), self._TL, self._TS)
        tiled_data = np.reshape(data, shape)

        # Stack in the samples direction
        shape = (size // (self._TL * self.NS), self.NS, self._TL)
        samples_stacked = np.moveaxis(
            np.moveaxis(tiled_data, 1, 2).reshape(shape), 1, 2)

        # Stack in the lines direction
        return np.reshape(samples_stacked, self.shape)

    @property
    def _bands(self):
        """Cube band bin header."""
        return self.header['BandBin']

    @property
    def bands(self):
        """Cube bands numbers."""
        return np.array(self._bands['OriginalBand'])

    @property
    def wvlns(self):
        """Cube central wavelengths (um)."""
        return np.array(self._bands['Center'])

    @property
    def _inst(self):
        """Cube instrument header."""
        return self.header['Instrument']

    @property
    def start(self):
        """Instrument start time (UTC)."""
        return dtime(self._inst['StartTime'])

    @property
    def stop(self):
        """Instrument stop time (UTC)."""
        return dtime(self._inst['StopTime'])

    @property
    def duration(self):
        """Instrument acquisition dureation."""
        return self.stop - self.start

    @property
    def time(self):  # noqa: D402
        """Instrument mid time (UTC)."""
        return self.start + self.duration / 2

    @property
    def _naif(self):
        """NAIF keywords stored in ISIS header."""
        return self.pvl['NaifKeywords']

    @property
    def exposure(self):
        """ISIS header exposure duration."""
        return self._inst['ExposureDuration']

    @property
    def kernels(self):
        """List of kernels cached by ISIS."""
        if 'Kernels' not in self:
            return None

        kernels = []
        for kernel in self.header['Kernels'].values():
            if isinstance(kernel, str) and '$' in kernel:
                kernels.append(kernel)
            elif isinstance(kernel, list):
                for k in kernel:
                    if '$' in k:
                        kernels.append(k)

        return kernels

    @property
    def target_name(self):
        """Main target name."""
        return self._inst['TargetName']

    @property
    def target_radii(self):
        """Main target radii (km)."""
        for k, v in self.__pvl['NaifKeywords']:
            if 'RADII' in k:
                return v
        raise ValueError('Target radii not found in the header.')

    @property
    def target_radius(self):
        """Main target mean radius (km)."""
        return np.power(np.prod(self.target_radii), 1 / 3)

    @property
    def original_labels(self):
        """Get original labels."""
        if self.__lbls is None:
            self.__lbls = ISISOriginalLabels(self.filename, self.pvl)
        return self.__lbls

    @property
    def _body_rotation(self):
        """Main target body rotation quaternion."""
        p = self.tables['BodyRotation'].data
        q0 = p['J2000Q0']
        q1 = p['J2000Q1']
        q2 = p['J2000Q2']
        q3 = p['J2000Q3']

        q = np.array([q0, q1, q2, q3]).flatten()

        return hat(q)

    @property
    def _sc_position(self):
        """Spacecraft position in the main target body frame."""
        p = self.tables['InstrumentPosition'].data
        x = p['J2000X']
        y = p['J2000Y']
        z = p['J2000Z']

        j2000 = np.array([x, y, z]).flatten()

        return q_rot(self._body_rotation, j2000)

    @property
    def _sun_position(self):
        """Sun position in the main target body frame."""
        p = self.tables['SunPosition'].data
        x = p['J2000X']
        y = p['J2000Y']
        z = p['J2000Z']

        j2000 = np.array([x, y, z]).flatten()

        return q_rot(self._body_rotation, j2000)

    @property
    def sc(self):
        """Sub-Spacecraft point (West Longitude, Latitude)."""
        return lonlat(self._sc_position)

    @property
    def ss(self):
        """Sub-solar point (West Longitude, Latitude)."""
        return lonlat(self._sun_position)
