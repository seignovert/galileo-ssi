"""Galileo SSI module to parse ISIS files."""

from .isis import ISISCube


class SSI(ISISCube):
    """Galileo Solid State Image System ISIS3 object.

    Parameters
    ----------
    filename: str
        Input SSI filename.

    """
    def __init__(self, filename):
        super().__init__(filename)

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
        ]))

    def __getitem__(self, name):
        """Return data array based on item name."""
        return self.cube[self._get_layer(name), :, :]

    @property
    def img_id(self):
        """Image ID based on filename."""
        return self.filename.split('.')[0]

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
        if name not in self.layers:
            raise ValueError(f'Layer `{name}` not found.')

        return self.layers.index(name)

    @property
    def data(self):
        """Image I/F data.

        Note
        ----
        By default the data are considered
        to be stored in the first band of the cube.

        """
        return self[self.filter_name]

    @property
    def phase(self):
        """Phase angle data (degree)."""
        return self['Phase Angle']

    @property
    def inc(self):
        """Incidence angle data (degree)."""
        return self['Incidence Angle']

    @property
    def emi(self):
        """Emission angle data (degree)."""
        return self['Emission Angle']

    @property
    def lon(self):
        """West longitude data (degree)."""
        return self['Longitude']

    @property
    def lat(self):
        """North latitude data (degree)."""
        return self['Latitude']

    @property
    def res(self):
        """Ground pixel resolution data (km/pixel)."""
        return self['Pixel Resolution']
