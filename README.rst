.. image:: https://img.shields.io/pypi/v/python-ulid.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-ulid
.. image:: https://img.shields.io/travis/mdomke/python-ulid/master.svg?style=flat-square
    :target: https://travis-ci.org/mdomke/python-ulid
.. image:: https://img.shields.io/pypi/l/python-ulid.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-ulid
.. image:: https://img.shields.io/codecov/c/github/mdomke/python-ulid.svg?style=flat-square
    :target: https://codecov.io/gh/mdomke/python-ulid


What is this?
=============

This is a port of the original JavaScript ULID_ implementation to Python.

A ULID is a *universally unique lexicographically sortable identifier*. It is

- 128-bit compatible with UUID
- 1.21e+24 unique ULIDs per millisecond
- Lexicographically sortable!
- Canonically encoded as a 26 character string, as opposed to the 36 character UUID
- Uses Crockford's base32 for better efficiency and readability (5 bits per character)
- Case insensitive
- No special characters (URL safe)

In general the structure of a ULID is as follows:

.. code-block:: txt

    01AN4Z07BY      79KA1307SR9X4MV3
    |----------|    |----------------|
     Timestamp          Randomness
       48bits             80bits


For more information have a look at the original specification_.

Basic Usage
-----------

.. code-block:: python

		>>> from ulid import ULID
		>>> ulid = ULID.new()
		>>> ulid.str
		'01BTGNYV6HRNK8K8VKZASZCFPE'
		>>> ulid.timestamp
		1505945939.153
		>>> ulid.datetime
		datetime.datetime(2017, 9, 20, 22, 18, 59, 153000)


Installation
------------

.. code-block:: bash

		$ pip install python-ulid


Other implementations
---------------------

- `ahawker/ulid <https://github.com/ahawker/ulid>`_
- `valohai/ulid2 <https://github.com/valohai/ulid2>`_
- `mdipierro/ulid <https://github.com/mdipierro/ulid>`_


.. _ULID: https://github.com/alizain/ulid
.. _specification: https://github.com/alizain/ulid#specification
