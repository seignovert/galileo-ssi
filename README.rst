Python parser for Galileo SSI instrument
========================================

Install
-------

With PIP:

.. code:: bash

    pip install galileo-ssi

From the source:

.. code:: bash

    python setup.py develop

Usage
-----

.. code:: python

    >>> from ssi import SSI

    >>> img = SSI('5126r_cal.pho.cub')

    >>> img.data
    array([[       nan,        nan, 0.6616845 , ..., 0.01874097, 0.02330439, 0.01920273],
           [       nan,        nan, 0.5667658 , ..., 0.64417607, 0.64331275, 0.62484866],
           [       nan,        nan, 0.5833956 , ..., 0.64018035, 0.6447313 , 0.6334495 ],
           ...,
           [       nan, 0.78587395, 0.796514  , ..., 0.5145454 , 0.48593405, 0.48256457],
           [1.0838959 , 0.84181863, 0.76158404, ..., 0.46052158, 0.44188383, 0.44267857],
           [5.486526  , 0.772195  , 0.7204898 , ...,        nan,        nan,       nan]],
    dtype=float32)"


See notebooks_ for more examples.

.. _notebooks: notebooks/
