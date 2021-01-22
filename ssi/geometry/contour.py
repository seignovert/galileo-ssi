"""Contouring module."""

import numpy as np


def edges(cond):
    """Compute internal edges on a conditional array.

    The array is displaced in all 4 direction to locate
    the internal edges and regroup together.

    Parameters
    ----------
    cond: numpy.ndarray
        Conditional mask array.

    Return
    ------
    numpy.ndarray
        Conditional internal edges.

    """
    h, w = np.shape(cond)

    # Create a mask with the an invalid condition border
    mask = np.zeros((h + 2, w + 2), dtype=np.int8)
    mask[1:-1, 1:-1] = cond

    top = mask[1:-1, 1:-1] - mask[:-2, 1:-1] > 0
    right = mask[1:-1, 1:-1] - mask[1:-1, 2:] > 0
    bottom = mask[1:-1, 1:-1] - mask[2:, 1:-1] > 0
    left = mask[1:-1, 1:-1] - mask[1:-1, :-2] > 0

    return top | right | bottom | left


def ls_contours(cntr, threshold=250):
    """Multi-contour contours indexes.

    Search iteratively all the contours in the mask.

    Parameters
    ----------
    cntr: np.ndarray
        Edges contour mask (see :py:func:`edges`).
    threshold: int, optional
        Minimum number of points in a contour (default 250).

    Returns
    --------
    [[lines, samples], …]
        List of all the contours.

    Raises
    ------
    ValueError
        If the number of polygons to contour is invalid.

    Note
    ----
    A threshold is apply to avoid contour on narrow
    portion of the image.
    If the remaining number of point in the contour is lower
    than that threshold, no more contour is searched.

    """
    ls = []
    for _ in range(np.sum(cntr)):
        lines, samples, cntr = ls_contour(cntr)

        if len(lines) > threshold:
            ls.append([lines, samples])

        if not np.max(cntr) or np.sum(cntr) < threshold:
            break
    else:
        raise ValueError('Too many polygons in the contour.')

    return ls


# Directions motion and next iteration for a clockwise circular permutation.
DIRECTIONS = np.array([                  # Origin -> Next iteration
    [-1, -1, [5, 6, 7, 0, 1, 2, 3, 4]],  # tl -> b
    [-1, 0, [6, 7, 0, 1, 2, 3, 4, 5]],   # t -> bl
    [-1, 1, [7, 0, 1, 2, 3, 4, 5, 6]],   # tr -> l
    [0, 1, [0, 1, 2, 3, 4, 5, 6, 7]],    # r -> tl
    [1, 1, [1, 2, 3, 4, 5, 6, 7, 0]],    # br -> t
    [1, 0, [2, 3, 4, 5, 6, 7, 0, 1]],    # b -> tr
    [1, -1, [3, 4, 5, 6, 7, 0, 1, 2]],   # bl -> r
    [0, -1, [4, 5, 6, 7, 0, 1, 2, 3]],   # l -> br
], dtype=object)


def ls_contour(cntr):
    """Extract one line and sample indexes contour.

    Parameters
    ----------
    cntr: np.ndarray
        Edges contour mask (see :py:func:`edges`).

    Returns
    --------
    list
        Contour line indexes.
    list
        Contour sample indexes.
    numpy.ndarray
        New contour without the selected contour.

    Raises
    ------
    ValueError
        If the number of polygons to contour is invalid.

    Note
    ----
    When the contour is found, the pixel selected are
    removed from the edges contour mask.

    """
    if not np.max(cntr):
        raise ValueError('The contour is empty')

    h, w = np.shape(cntr)

    # Find the first valid point
    l0, s0 = np.unravel_index(np.argmax(cntr), cntr.shape)

    # Init path position and direction
    l, s, v = l0, s0, [0, 1, 2, 3, 4, 5, 6, 7]

    # Save initial point
    lines, samples = [l0], [s0]

    npts = 2 * np.sum(cntr)

    for _ in range(npts):
        for dl, ds, v in DIRECTIONS[v]:
            if (0 <= l + dl < h) and (0 <= s + ds < w) and cntr[l + dl, s + ds]:
                l, s = l + dl, s + ds
                lines.append(l)
                samples.append(s)
                break

        if l == l0 and s == s0:
            break
    else:
        raise ValueError('Path can not be closed property')

    # Remove the point that where found
    cntr[lines, samples] = False

    return lines, samples, cntr
