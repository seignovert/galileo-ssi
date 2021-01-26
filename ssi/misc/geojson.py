"""GeoJson module."""

from json import dumps

from collections import UserDict

import numpy as np


PRECISION = 2


class GeoJsonDict(UserDict):
    """GeoJson generic object.

    Parameters
    ----------
    prec: int, optional
        Float rounding precision.

    """

    def __init__(self, prec=PRECISION):
        self.data = {
            'type': self.__class__.__name__,
        }
        self.prec = prec

    def round(self, value):
        """Round floats."""
        return round(float(value), self.prec)

    @property
    def json(self):
        return dumps(self.data, default=lambda x: x.data)


class Point(GeoJsonDict):
    """GeoJson point geometry."""

    def __init__(self, *args, prec=PRECISION):
        super().__init__(prec=prec)

        if len(args) == 1:
            lon_e, lat = args[0]
        elif len(args) == 2:
            lon_e, lat = args
        else:
            raise ValueError('Invalid coordinates input.')

        self['coordinates'] = [
            self.round(lon_e),
            self.round(lat),
        ]


class LineString(GeoJsonDict):
    """GeoJson line string geometry."""

    def __init__(self, *args, prec=PRECISION):
        super().__init__(prec=prec)

        if len(args) == 1:
            vertices = args[0]
        elif len(args) == 2:
            vertices = np.transpose(args[:2])
        else:
            raise ValueError('Invalid coordinates input.')

        self['coordinates'] = [
            [self.round(lon_e), self.round(lat)]
            for lon_e, lat in vertices
        ]


class Polygon(GeoJsonDict):
    """GeoJson polygon geometry."""

    def __init__(self, *args, prec=PRECISION):
        super().__init__(prec=prec)

        if len(args) == 1:
            polygon = args[0]
        elif len(args) == 2:
            polygon = np.transpose(args[:2])
        else:
            raise ValueError('Invalid coordinates input.')

        # Check polygon dimensions
        ndim = np.ndim(polygon)

        if ndim == 2:
            polygon = [polygon]
        elif ndim in (1, 3):
            pass
        else:
            raise ValueError('Invalid coordinates format')

        self['coordinates'] = [
            [
                [self.round(lon_e), self.round(lat)]
                for lon_e, lat in vertices
            ] for vertices in polygon
        ]


class MultiPoint(LineString):
    """GeoJson multi points geometry."""


class MultiLineString(Polygon):
    """GeoJson multi line strings geometry."""


class MultiPolygon(GeoJsonDict):
    """GeoJson multi polygon geometry."""

    def __init__(self, polygons, prec=PRECISION):
        super().__init__(prec=prec)

        self['coordinates'] = [
            [
                [
                    [self.round(lon_e), self.round(lat)]
                    for lon_e, lat in vertices
                ] for vertices in polygon
            ] for polygon in polygons
        ]


GEOMETRIES = {
    'point': Point,
    'line': LineString,
    'linestring': LineString,
    'polygon': Polygon,
    'multipoint': MultiPoint,
    'multiline': MultiLineString,
    'multilinestring': MultiLineString,
    'multipolygon': MultiPolygon,
}


class Feature(GeoJsonDict):
    """GeoJson feature object."""

    def __init__(self, prec=PRECISION, **kwargs):
        super().__init__(prec=prec)

        for key, value in kwargs.items():
            if key.lower() in GEOMETRIES:
                self['geometry'] = GEOMETRIES[key.lower()](value, prec=prec)
            else:
                if 'properties' not in self:
                    self['properties'] = {}

                if isinstance(value, (float, np.inexact)):
                    self['properties'][key] = self.round(value)
                elif isinstance(value, np.integer):
                    self['properties'][key] = int(value)
                else:
                    self['properties'][key] = value


class GeoJson:
    """Polymorphic GeoJson object."""
    def __new__(cls, prec=PRECISION, **kwargs):
        if len(kwargs) == 1:
            for key, value in kwargs.items():
                if key.lower() in GEOMETRIES:
                    return GEOMETRIES[key.lower()](value, prec=prec)
                else:
                    raise KeyError('No geometry was provided.')

        return Feature(prec=prec, **kwargs)
