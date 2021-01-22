"""Test GeoJson module."""

import numpy as np

from pytest import raises

from ssi.misc.geojson import (Feature, GeoJson, LineString, MultiLineString,
                              MultiPoint, MultiPolygon, Point, Polygon)


def test_geojson_pt():
    """Test GeoJson Point."""
    assert Point([100, 0]) == {
        'type': 'Point',
        'coordinates': [100.0, 0.0],
    }

    assert Point(100, 0) == {
        'type': 'Point',
        'coordinates': [100.0, 0.0],
    }

    with raises(ValueError):
        _ = Point(1, 2, 3)


def test_geojson_line():
    """Test GeoJson line string."""
    res = {
        'type': 'LineString',
        'coordinates': [
             [100.0, 0.0],
             [101.0, 1.0],
         ],
    }

    # List of vertices
    assert LineString([[100.0, 0.0], [101.0, 1.0]]) == res

    # List of east longitude and latitudes
    assert LineString([100.0, 101.0], [0.0, 1.0]) == res

    with raises(ValueError):
        _ = LineString(1, 2, 3)


def test_geojson_polygon_no_holes():
    """Test GeoJson Polygon without holes."""
    res = {
        'type': 'Polygon',
        'coordinates': [
             [
                 [100.0, 0.0],
                 [101.0, 0.0],
                 [101.0, 1.0],
                 [100.0, 1.0],
                 [100.0, 0.0],
             ]
         ],
    }

    # List of vertices
    assert Polygon([
                 [100.0, 0.0],
                 [101.0, 0.0],
                 [101.0, 1.0],
                 [100.0, 1.0],
                 [100.0, 0.0],
             ]) == res

    assert Polygon([[
                 [100.0, 0.0],
                 [101.0, 0.0],
                 [101.0, 1.0],
                 [100.0, 1.0],
                 [100.0, 0.0],
             ]]) == res

    # List of east longitude and latitudes
    assert Polygon(
        [100.0, 101.0, 101.0, 100.0, 100.0],
        [0.0, 0.0, 1.0, 1.0, 0.0],
    ) == res

    with raises(ValueError):
        _ = Polygon(1, 2, 3)

    with raises(ValueError):
        _ = Polygon(1)


def test_geojson_polygon_with_holes():
    """Test GeoJson Polygon with holes."""
    assert Polygon([[
                 [100.0, 0.0],
                 [101.0, 0.0],
                 [101.0, 0.5],
                 [101.0, 1.0],
                 [100.0, 1.0],
                 [100.0, 0.0],
             ],
             [
                 [100.8, 0.8],
                 [100.8, 0.2],
                 [100.2, 0.2],
                 [100.2, 0.8],
                 [100.8, 0.8],
             ]]) == {
        'type': 'Polygon',
        'coordinates': [
             [
                 [100.0, 0.0],
                 [101.0, 0.0],
                 [101.0, 0.5],
                 [101.0, 1.0],
                 [100.0, 1.0],
                 [100.0, 0.0],
             ],
             [
                 [100.8, 0.8],
                 [100.8, 0.2],
                 [100.2, 0.2],
                 [100.2, 0.8],
                 [100.8, 0.8],
             ],
         ],
    }


def test_geojson_multi_pts():
    """Test GeoJson multi points."""
    res = {
        'type': 'MultiPoint',
        'coordinates': [
             [100.0, 0.0],
             [101.0, 1.0],
         ],
    }

    # List of vertices
    assert MultiPoint([[100.0, 0.0], [101.0, 1.0]]) == res

    # List of east longitude and latitudes
    assert MultiPoint([100.0, 101.0], [0.0, 1.0]) == res


def test_geojson_multi_lines():
    """Test GeoJson multi line strings."""
    # List of vertices
    assert MultiLineString([
                 [100.0, 0.0],
                 [101.0, 1.0],
                 [102.0, 2.0],
                 [103.0, 3.0],
             ]) == {
        'type': 'MultiLineString',
        'coordinates': [
             [
                 [100.0, 0.0],
                 [101.0, 1.0],
                 [102.0, 2.0],
                 [103.0, 3.0],
             ]
         ],
    }

    assert MultiLineString([
             [
                 [100.0, 0.0],
                 [101.0, 1.0],
             ],
             [
                 [102.0, 2.0],
                 [103.0, 3.0],
             ],
         ]) == {
        'type': 'MultiLineString',
        'coordinates': [
             [
                 [100.0, 0.0],
                 [101.0, 1.0],
             ],
             [
                 [102.0, 2.0],
                 [103.0, 3.0],
             ]
         ],
    }


def test_geojson_multi_polygons():
    """Test GeoJson multi polygon strings."""
    # List of vertices
    assert MultiPolygon([
             [
                 [
                     [102.0, 2.0],
                     [103.0, 2.0],
                     [103.0, 3.0],
                     [102.0, 3.0],
                     [102.0, 2.0],
                 ],
             ],
             [
                 [
                     [100.0, 0.0],
                     [101.0, 0.0],
                     [101.0, 1.0],
                     [100.0, 1.0],
                     [100.0, 0.0],
                 ],
                 [
                     [100.2, 0.2],
                     [100.2, 0.8],
                     [100.8, 0.8],
                     [100.8, 0.2],
                     [100.2, 0.2],
                 ],
             ],
         ]) == {
        'type': 'MultiPolygon',
        'coordinates': [
             [
                 [
                     [102.0, 2.0],
                     [103.0, 2.0],
                     [103.0, 3.0],
                     [102.0, 3.0],
                     [102.0, 2.0],
                 ],
             ],
             [
                 [
                     [100.0, 0.0],
                     [101.0, 0.0],
                     [101.0, 1.0],
                     [100.0, 1.0],
                     [100.0, 0.0],
                 ],
                 [
                     [100.2, 0.2],
                     [100.2, 0.8],
                     [100.8, 0.8],
                     [100.8, 0.2],
                     [100.2, 0.2],
                 ],
             ],
         ],
    }


def test_geojson_feature():
    """Test GeoJson feature."""
    assert Feature(
        line = [
            [100.0, 0.0],
            [101.0, 1.0],
        ],
        color = 'blue'
    ) == {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [
                [100.0, 0.0],
                [101.0, 1.0],
            ]
        },
        'properties': {
            'color': 'blue',
        }
    }

    assert Feature(
        polygon = [
            [100.0, 0.0],
            [101.0, 1.0],
        ],
        color = 'red'
    ) == {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
                [
                    [100.0, 0.0],
                    [101.0, 1.0],
                ]
            ]
        },
        'properties': {
            'color': 'red',
        }
    }


def test_geojson_polymorph():
    """Test GeoJson polymorph form."""
    assert GeoJson(
        line=[
            [100.0001, 0.0],
            [101.0, 1.0],
        ],
        color = 'blue',
        stroke = np.int32(1),
        alpha = 0.50005,
    ) == {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [
                [100.0, 0.0],
                [101.0, 1.0],
            ],
        },
        'properties': {
            'color': 'blue',
            'stroke': 1,
            'alpha': 0.5,
        }
    }

    assert GeoJson(polygon=[
        [100.0001, 0.0],
        [101.0, 1.0],
    ], color='blue') == {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
                [
                    [100.0, 0.0],
                    [101.0, 1.0],
                ]
            ],
        },
        'properties': {
            'color': 'blue'
        }
    }

    assert GeoJson(point=[100.0, 0.0]) == {
        'type': 'Point',
        'coordinates': [100.0, 0.0],
    }

    with raises(KeyError):
        _ = GeoJson(color='blue')


def test_geojson_json():
    """Test GeoJson to JSON serialization."""
    assert GeoJson(point=[100.0, 0.0]).json == \
        '{"type": "Point", "coordinates": [100.0, 0.0]}'

    assert GeoJson(polygon=[
        [100.0001, 0.0],
        [101.0, 1.0],
    ], color='blue').json == (
        '{"type": "Feature", "geometry": '
        '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 1.0]]]}, '
        '"properties": {"color": "blue"}}'
    )
