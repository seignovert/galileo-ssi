"""Photometric module."""

import numpy as np

from matplotlib.path import Path


def fit_minnaert(i_f, mu0, mu1, err=False, debug=False):
    """Simplified Minnaert photometric equation.

    I/F = B₀ * μ₀ ^ k * μ₁ ^ (k - 1)

    => log(I/F) + log(μ₁) = k * (log(μ₀) + log(μ₁)) + log(B₀)

    Parameters
    ----------
    i_f: array
        Reflectance (I/F) with I the intensity of scattered sunlight
        at a point on the disk, and πF is the incident solar flux.
    mu0: array
        The cosine of the incidence angle.
    mu1: array
        The cosine of the emission angle.
    err: bool, optional
        Retrieve error parameter (1σ).
    debug: bool, optional
        Enable fit debugging.

    Returns
    -------
    B0: float
        The normal reflectance of the surface (at phase α=0°).
    k: float
        A dark surface would have k equal to, or close to, 0.5.
        An ideal Lambert surface would have k = 1
    (xdata, ydata): (array, array), optional
        On ``debug=TRUE``, reduce (x, y) data.
    (xfit, yfit): ([float, float], [float, float]), optional
        On ``debug=TRUE``, fitted (x, y) line.

    Source
    ------
    * Buratti et al. 1983 (doi:10.1016/0019-1035(83)90053-2)

    """
    xdata = np.log(mu0) + np.log(mu1)
    ydata = np.log(i_f) + np.log(mu1)

    (a, b), cov = np.polyfit(xdata, ydata, 1, cov=True)
    da, db = np.sqrt(np.diag(cov))

    B0, k = np.exp(b), a
    if err:
        dB0, dk = B0 * db, da

    if not debug:
        return (B0, k) if not err else (B0, k, dB0, dk)

    xmin, xmax = np.nanmin(xdata), np.nanmax(xdata)

    if not err:
        return (B0, k), (xdata, ydata), ([xmin, xmax], [a * xmin + b, a * xmax + b])

    return (B0, k, dB0, dk), (xdata, ydata), (
        [xmin, xmax], [a * xmin + b, a * xmax + b],
        Path([
            (xmin, (a + da) * xmin + (b + db)),
            (xmax, (a + da) * xmax + (b + db)),
            (xmax, (a - da) * xmax + (b - db)),
            (xmin, (a - da) * xmin + (b - db)),
            (xmin, (a + da) * xmin + (b + db)),
        ])
    )


def fit_hapke(i_f, mu0, mu1, err, debug=False):
    """Simplified Hapke photometric equation.

    I/F = A * μ₀ / (μ₀ + μ₁) * f(α) + B * μ₀

    with B = 1 - A

    => 1 - I/F / μ₀ - 1 = - A * f(α) / (μ₀ + μ₁) + A

    Parameters
    ----------
    i_f: array
        Reflectance (I/F) with I the intensity of scattered sunlight
        at a point on the disk, and πF is the incident solar flux.
    mu0: array
        The cosine of the incidence angle.
    mu1: array
        The cosine of the emission angle.
    err: bool, optional
        Retrieve error parameter (1σ).
    debug: bool, optional
        Enable fit debugging.

    Returns
    -------
    A: float
        Surface phase scattering behavior parameter:
        * A = 1: Lunar-like scattering.
        * A = 0: Lambert-like scattering.
    f_alpha: float
        Phase function parameter.
    (xdata, ydata): (array, array), optional
        On ``debug=TRUE``, reduce (x, y) data.
    (xfit, yfit): ([float, float], [float, float]), optional
        On ``debug=TRUE``, fitted (x, y) line.

    Source
    ------
    * Buratti et al. 1983 (doi:10.1016/0019-1035(83)90053-2)

    """
    xdata = 1 / np.add(mu0, mu1)
    ydata = np.divide(i_f, mu0) - 1

    (a, b), cov = np.polyfit(xdata, ydata, 1, cov=True)
    da, db = np.sqrt(np.diag(cov))

    A, f_alpha = -b, -a / b
    if err:
        dA, df_alpha = db, f_alpha * np.sqrt((da / a) ** 2 + (db / b) ** 2)

    if not debug:
        return (A, f_alpha) if not err else (A, f_alpha, dA, df_alpha)

    xmin, xmax = np.nanmin(xdata), np.nanmax(xdata)

    if not err:
        return (A, f_alpha), (xdata, ydata), ([xmin, xmax], [a * xmin + b, a * xmax + b])

    return (A, f_alpha, dA, df_alpha), (xdata, ydata), (
        [xmin, xmax], [a * xmin + b, a * xmax + b],
        Path([
            (xmin, (a + da) * xmin + (b + db)),
            (xmax, (a + da) * xmax + (b + db)),
            (xmax, (a - da) * xmax + (b - db)),
            (xmin, (a - da) * xmin + (b - db)),
            (xmin, (a + da) * xmin + (b + db)),
        ])
    )


def fit(img, cond, model='minnaert', err=False, debug=False):
    """Fit SSI data with a photometric model.

    Parameters
    ----------
    img: SSI
        SSI-like image object.
    cond: np.ndarray
        Conditional array.
    model: str, optional
        Photometric model to use.
        Only ``minnaert`` and ``hapke`` are available.
    err: bool, optional
        Retrieve error parameter (1σ).
    debug: bool, optional
        Enable fit debugging.

    Returns
    -------
    float, float
        Photometric parameters from the selected model:
            * (B0, k) for ``minnaert``.
            * (A, f_alpha) for ``hapke``.
    (xdata, ydata): (array, array), optional
        On ``debug=TRUE``, reduce (x, y) data.
    (xfit, yfit): ([float, float], [float, float]), optional
        On ``debug=TRUE``, fitted (x, y) line.

    Raises
    ------
    ValueError
        If the provided model is unknown.

    """
    if model.lower() == 'minnaert':
        return fit_minnaert(img.data[cond], img.mu0[cond], img.mu1[cond],
                            err=err, debug=debug)

    if model.lower() == 'hapke':
        return fit_hapke(img.data[cond], img.mu0[cond], img.mu1[cond],
                         err=err, debug=debug)

    raise ValueError(
        f'Unknown model=`{model}`. Only `minnaert` and `hapke` are available yet.')
