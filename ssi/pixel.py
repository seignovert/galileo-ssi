"""SSI pixel module."""

class SSIPixel:
    """SSI pixel object.

    Paramters
    ---------
    cube: ssi.SSI
        Parent cube object.
    s: int
        Sample position (``1`` to ``NS``).
    l: int
        Line position (``1`` to ``NL``).


    """
    def __init__(self, cube, s, l):
        self.__cube = cube
        self.s = s
        self.l = l

    def __str__(self):
        return f'{self.__cube}-S{self.s}_L{self.l}'

    def __repr__(self):
        return '\n - '.join([
            f'<{self.__class__.__name__}> {self}',
            f'Sample: {self.s}',
            f'Line: {self.l}',
            f'I/F: {self.data:.2e}',
            f'Lon: {self.lon:.1f}°W',
            f'Lat: {self.lat:.1f}°N',
            f'Inc: {self.inc:.1f}°',
            f'Emi: {self.emi:.1f}°',
            f'Phase: {self.phase:.1f}°',
            f'Res: {self.phase:.1f} km/pix',
        ])

    def __eq__(self, item):
        try:
            return str(self) == str(item)
        except TypeError:
            return False

    @property
    def s(self):
        """Pixel sample position."""
        return self.__s

    @s.setter
    def s(self, sample):
        """Sample value setter.

        Raises
        ------
        IndexError
            If the sample is outside the image range.

        """
        if not isinstance(sample, int):
            raise IndexError(f'Sample `{sample}` must be an integer.')

        if not 1 <= sample <= self.__cube.NS:
            raise IndexError(
                f'Sample `{sample}` invalid. Must be between 1 and {self.__cube.NS}')

        self.__s = sample

    @property
    def l(self):
        """Pixel lines position."""
        return self.__l

    @l.setter
    def l(self, line):
        """Line value setter.

        Raises
        ------
        IndexError
            If the line is outside the image range.

        """
        if not isinstance(line, int):
            raise IndexError(f'Line `{line}` must be an integer.')

        if not 1 <= line <= self.__cube.NL:
            raise IndexError(
                f'Line `{line}` invalid. Must be between 1 and {self.__cube.NL}')

        self.__l = line

    @property
    def data(self):
        """Pixel intensity (I/F)."""
        return self.__cube.data[self.s, self.l]

    @property
    def lon(self):
        """Pixel West longitude (deg)."""
        return self.__cube.lon[self.s, self.l]

    @property
    def lon_e(self):
        """Pixel East longitude (deg)."""
        return self.__cube.lon_e[self.s, self.l]

    @property
    def lat(self):
        """Pixel latitude (deg)."""
        return self.__cube.lat[self.s, self.l]

    @property
    def inc(self):
        """Pixel local incidence angle (degrees)."""
        return self.__cube.inc[self.s, self.l]

    @property
    def emi(self):
        """Pixel local emission angle (degrees)."""
        return self.__cube.emi[self.s, self.l]

    @property
    def phase(self):
        """Pixel local phase angle (degrees)."""
        return self.__cube.phase[self.s, self.l]

    @property
    def res(self):
        """Ground pixel resolution (km/pixel)."""
        return self.__cube.res[self.s, self.l]
