"""Galileo SSI module to parse ISIS files."""

from pathlib import Path as Pathlib

import numpy as np

from matplotlib.patches import PathPatch
from matplotlib.path import Path

from .align import corr_offset, img_offset
from .isis import ISISCube
from .geometry.contour import edges, ls_contours
from .misc import GeoJson
from .pixel import SSIPixel


MS = {
    'ms': 1,
    'millisecs': 1,
    'millisecondes': 1,
    's': 1000,
    'sec': 1000,
    'seconds': 1000,
}


class SSI(ISISCube):
    """Galileo Solid State Image System ISIS3 object.

    Parameters
    ----------
    filename: str
        Input SSI filename.
    align: bool, optional
        Enable data auto-alignment.
    offset_s: int, optional
        Provide sample offset to apply to the data.
    offset_l: int, optional
        Provide line offset to apply to the data.

    """

    def __init__(self, filename, align=False, offset_s=None, offset_l=None):
        super().__init__(filename)
        self.alignment(align=align, offset_s=offset_s, offset_l=offset_l)

    def __str__(self):
        return self.img_id

    def __repr__(self):
        return ('\n - '.join([
            f'<{self.__class__.__name__}> Cube: {self}',
            f'Size: {self.NS, self.NL}',
            f'Start time: {self.start}',
            f'Filter name: {self.filter_name}',
            f'Exposure: {self.exposure[0]} {self.exposure[1]}',
            f'Main target: {self.target_name}',
            f'Data alignment: {self.offset}',
        ]))

    def __getitem__(self, val):
        """Return data array based on value name or index."""
        if isinstance(val, str):
            ilayer = self._get_layer(val)
            data = self.cube[ilayer, :, :]

            return img_offset(data,
                              offset=self.offset,
                              is_data=(val == 'Data'))

        if isinstance(val, tuple):
            return SSIPixel(self, *val)

        raise IndexError('\n - '.join([
            'Invalid format. Use:',
            'STR -> Band image',
            '[INT, INT] -> Sample, Line pixel',
            '[SLICE, SLICE] -> Sample, Line data',
        ]))

    @property
    def img_id(self):
        """Image ID based on filename."""
        return Pathlib(self.filename).name.replace('_', '.').split('.')[0]

    @property
    def size(self):
        """Image size."""
        return (self.NL, self.NS)

    @property
    def filter_name(self):
        """Filter name."""
        return self._bands['FilterName']

    @property
    def target_name(self):
        """Main target name."""
        return self._inst['TargetName']

    @property
    def extent(self):
        """Pyplot imshow cube extent."""
        return [.5, self.NS + .5, self.NL + .5, .5]

    @property
    def cextent(self):
        """Pyplot contour cube extent."""
        return [.5, self.NS + .5, .5, self.NL + .5]

    @property
    def sticks(self):
        """Cube sample ticks."""
        return [1, self.NS // 4, self.NS // 2,
                self.NS // 4 + self.NS // 2, self.NS]

    @property
    def lticks(self):
        """Cube line ticks."""
        return [1, self.NL // 4, self.NL // 2,
                self.NL // 4 + self.NL // 2, self.NL]

    @property
    def slabel(self):
        """Cube sample label."""
        return 'Samples'

    @property
    def llabel(self):
        """Cube line label."""
        return 'Lines'

    @property
    def layers(self):
        """List the name of the layer available."""
        return self._bands['Name']

    def _get_layer(self, name):
        """Get layer index.

        Parameters
        ----------
        name: str
            Name of the layer to extract.

        Returns
        -------
        int
            Layer index in the cube.

        Raises
        ------
        ValueError
            If the :py:attr:`name` is not available in the cube.

        """
        if name == 'Data':
            name = self.filter_name

        if name not in self.layers:
            raise ValueError(f'Layer `{name}` not found.')

        return self.layers.index(name)

    @property
    def data(self):
        """Image I/F data.

        Note
        ----
        Use the ``FilterName`` to determine
        the band location of the data.

        """
        return self['Data']

    @property
    def phase(self):
        """Phase angle data (degree)."""
        return self['Phase Angle']

    @property
    def phase_angle(self):
        """Image mean phase angle data (degree)."""
        return np.nanmean(self.phase)

    @property
    def inc(self):
        """Incidence angle data (degree)."""
        return self['Incidence Angle']

    @property
    def emi(self):
        """Emission angle data (degree)."""
        return self['Emission Angle']

    @property
    def lon_e(self):
        """East longitude data (degree)."""
        return self['Longitude']

    @property
    def lon(self):
        """West longitude data (degree)."""
        return - self.lon_e % 360

    @property
    def lat(self):
        """North latitude data (degree)."""
        return self['Latitude']

    @property
    def res(self):
        """Ground pixel resolution data (km/pixel)."""
        return self['Pixel Resolution']

    @property
    def limb(self):
        """Navigation limb pixels."""
        return np.isnan(self.inc)

    @property
    def ground(self):
        """Navigation ground pixels."""
        return ~self.limb

    @property
    def mu0(self):
        """Incidence cosine angle."""
        return np.cos(np.radians(self.inc))

    @property
    def mu1(self):
        """Emission cosine angle."""
        return np.cos(np.radians(self.emi))

    @property
    def sample(self):
        """Samples grid."""
        return np.broadcast_to(
            np.arange(1, self.NS + 1), (self.NL, self.NS))

    @property
    def line(self):  # noqa: E743
        """Lines grid."""
        return np.broadcast_to(
            np.arange(1, self.NL + 1)[:, None], (self.NL, self.NS))

    @property
    def _corr_s(self):
        """Image correlation offset in sample direction."""
        return corr_offset(self.data, self.ground, axis=0)

    @property
    def _corr_l(self):
        """Image correlation offset in line direction."""
        return corr_offset(self.data, self.ground, axis=1)

    def alignment(self, align=True, offset_s=None, offset_l=None):
        """Align navigation data on the I/F data."""
        self.offset = False

        if align or offset_s is not None or offset_l is not None:
            offset_s = int(offset_s) if offset_s is not None else self._corr_s
            offset_l = int(offset_l) if offset_l is not None else self._corr_l

            self.offset = (offset_s, offset_l)

        return self.offset

    @property
    def offset_s(self):
        """Offset in sample direction."""
        return 0 if not self.offset else self.offset[0]

    @property
    def offset_l(self):
        """Offset in line direction."""
        return 0 if not self.offset else self.offset[1]

    @property
    def spacecraft_name(self):
        """Spacecraft name."""
        name = self._inst['SpacecraftName']
        return name.replace(' Orbiter', '').replace('_', ' ').title()

    @property
    def date(self):
        """Acquisition date."""
        return self.start.date()

    @property
    def expo_ms(self):
        """Acquisition exposure in millisecondes."""
        return self.exposure[0] * MS[self.exposure[1]]

    @property
    def valid_pixels(self):
        """Valid pixels mask.

        A pixel is considered as valid if its photometrically
        is defined and and have a defined ground coordinate.

        Here only the longitude is checked to exclude the limb
        pixels.

        """
        return ~np.isnan(self.data) & ~np.isnan(self.lon)

    @property
    def contours_ls(self):
        """List of the image contours line and sample indexes."""
        return ls_contours(edges(self.valid_pixels))

    @property
    def contours_coordinates(self):
        """List of the image contours coordinates."""
        lons_e = np.array(self.lon_e, dtype=np.float)
        lats = np.array(self.lat, dtype=np.float)

        return [
            np.transpose([lons_e[lines, samples], lats[lines, samples]])
            for lines, samples in self.contours_ls
        ]

    @property
    def contour_path(self):
        """List of the image contours coordinates."""
        vertices, codes = [], []
        for coordinates in self.contours_coordinates:
            for lon_e, lat in coordinates:
                vertices.append((lon_e, lat))

            npts = len(coordinates)
            codes += [Path.MOVETO] + (npts - 2) * [Path.LINETO] + [Path.CLOSEPOLY]

        return Path(vertices, codes)

    def contour(self, **kwargs):
        """Get patch based on the image contour."""
        return PathPatch(self.contour_path, **kwargs)

    def geojson(self, fout=None, prec=3, overwrite=False):
        """Export image contour as a geojson."""
        geojson = GeoJson(
            img_id=self.img_id,
            start_time=self.start.strftime('%Y-%m-%dT%H:%M:%S'),
            main_target=self.target_name,
            NS=self.NS,
            NL=self.NL,
            filter=self.filter_name,
            expo_duration_ms=self.expo_ms,
            mean_res_m=np.nanmean(self.res.data),
            res_m_min=np.nanmin(self.res.data),
            res_m_max=np.nanmax(self.res.data),
            inc_min=np.nanmin(self.inc.data),
            inc_max=np.nanmax(self.inc.data),
            emi_min=np.nanmin(self.emi.data),
            emi_max=np.nanmax(self.emi.data),
            phase_min=np.nanmin(self.phase.data),
            phase_max=np.nanmax(self.phase.data),
            offset_l=self.offset_l,
            offset_s=self.offset_s,
            polygon=self.contours_coordinates,
            prec=prec,
        )

        if fout is None:
            return geojson

        fout = Pathlib(fout)
        fname = fout / (self.img_id + '.geojson')

        if fname.exists() and not overwrite:
            raise FileExistsError(fname)

        # Create output folder if missing
        fname.parent.mkdir(parents=True, exist_ok=True)

        fname.write_text(geojson.json)

        return fname
