.. image:: logo.png
    :width: 360px
    :align: center

.. image:: https://img.shields.io/pypi/v/python-ulid.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-ulid
.. image:: https://img.shields.io/travis/mdomke/python-ulid/master.svg?style=flat-square
    :target: https://travis-ci.org/mdomke/python-ulid
.. image:: https://img.shields.io/pypi/l/python-ulid.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-ulid
.. image:: https://img.shields.io/codecov/c/github/mdomke/python-ulid.svg?style=flat-square
    :target: https://codecov.io/gh/mdomke/python-ulid
.. image:: https://readthedocs.org/projects/python-ulid/badge/?version=latest&style=flat-square
    :target: https://python-ulid.readthedocs.io
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
    :target: https://black.readthedocs.io/en/stable/index.html


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

Installation
------------

.. code-block:: bash

  $ pip install python-ulid

Basic Usage
-----------

.. code-block:: python

  >>> from ulid import ULID
  >>> ulid = ULID()
  >>> str(ulid)
  '01BTGNYV6HRNK8K8VKZASZCFPE'
  >>> ulid.timestamp
  1505945939.153
  >>> ulid.datetime
  datetime.datetime(2017, 9, 20, 22, 18, 59, 153000, tzinfo=datetime.timezone.utc)
  >>> ulid.hex
  '015ea15f6cd1c56689a373fab3f63ece'
  >>> ulid.to_uuid()
  UUID('015ea15f-6cd1-c566-89a3-73fab3f63ece')


Other implementations
---------------------

- `ahawker/ulid <https://github.com/ahawker/ulid>`_
- `valohai/ulid2 <https://github.com/valohai/ulid2>`_
- `mdipierro/ulid <https://github.com/mdipierro/ulid>`_


Changelog
=========

Version 1.0.0
-------------

- Dropped support for Python 2. Only Python 3.6+ is supported.
- Added type annotations
- Added the named constructors `ULID.from_datetime`, `ULID.from_timestamp` and `from_hex`.
- The named constructor `ULID.new` has been removed. Use one of the specifc named constructors
  instead. For a new `ULID` created from the current timestamp use the standard constructor.

.. code-block:: python

  # old
  ulid = ULID.new()
  ulid = ULID.new(time.time())
  ulid = ULID.new(datetime.now())

  # new
  ulid = ULID()
  ulid = ULID.from_timestamp(time.time())
  ulid = ULID.from_datetime(datetime.now())

- The `ULID.str` and `ULID.int` methods have been removed in favour of the more Pythonic special
  dunder-methods. Use `str(ulid)` and `int(ulid)` instead.
- Added the property `ULID.hex` that returns a hex representation of the `ULID`.

.. code-block:: python

  >>> ULID().hex
  '0171caa5459a8631a6894d072c8550a8'

- Equality checks and ordering now also work with `str`-instances.
- The package now has no external dependencies.
- The test-coverage has been raised to 100%.


.. _ULID: https://github.com/alizain/ulid
.. _specification: https://github.com/alizain/ulid#specification
