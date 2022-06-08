.. raw:: html

   <p align="center">
      <br />
      <a href=""https://python-ulid.readthedocs.io>
         <img src="./logo.png" width="360" alt="ulid" />
      </a>
      <br />
      <br />
      <br />
   </p>
   <p align="center">
      <a href="https://pypi.python.org/pypi/python-ulid">
         <img src="https://img.shields.io/pypi/v/python-ulid.svg?style=flat-square" />
      </a>
      <a href="https://codecov.io/gh/mdomke/python-ulid">
         <img src="https://img.shields.io/codecov/c/github/mdomke/python-ulid.svg?style=flat-square" />
      </a>
      <a href="https://github.com/mdomke/python-ulid/actions?query=workflow%3Alint-and-test">
         <img src="https://img.shields.io/github/workflow/status/mdomke/python-ulid/lint-and-test?style=flat-square" />
      </a>
      <a href="https://python-ulid.readthedocs.io">
         <img src="https://readthedocs.org/projects/python-ulid/badge/?version=latest&style=flat-square" />
      </a>
      <a href="https://black.readthedocs.io/en/stable/index.html">
         <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" />
      </a>
   </p>


.. teaser-begin

A ``ULID`` is a *universally unique lexicographically sortable identifier*. It is

* 128-bit compatible with ``UUID``
* 1.21e+24 unique ULIDs per millisecond
* Lexicographically sortable!
* Canonically encoded as a 26 character string, as opposed to the 36 character UUID
* Uses Crockford's base32 for better efficiency and readability (5 bits per character)
* Case insensitive
* No special characters (URL safe)

In general the structure of a ULID is as follows:

.. code-block:: text

   01AN4Z07BY      79KA1307SR9X4MV3
  |----------|    |----------------|
   Timestamp          Randomness
     48bits             80bits


For more information have a look at the original
`specification <https://github.com/alizain/ulid#specification>`_.

.. teaser-end

.. installation-begin

Installation
------------

Use ``pip`` to install the library

.. code-block:: bash

  $ pip install python-ulid

.. installation-end

.. usage-begin

Basic Usage
-----------

Create a new ``ULID`` object from the current timestamp

.. code-block:: pycon

   >>> from ulid import ULID
   >>> ULID()
   ULID(01E75HZVW36EAZKMF1W7XNMSB4)

or use one of the named constructors

.. code-block:: pycon

   >>> import time, datetime
   >>> ULID.from_timestamp(time.time())
   ULID(01E75J1MKKWMGG0N5MBHFMRC84)
   >>> ULID.from_datetime(datetime.datetime.now())
   ULID(01E75J2XBK390V2XRH44EHC10X)

There are several options for encoding the ``ULID`` object (e.g. string, hex, int),
as well as to access the timestamp attribute in different formats:

.. code-block:: pycon

   >>> str(ulid)
   '01BTGNYV6HRNK8K8VKZASZCFPE'
   >>> ulid.hex
   '015ea15f6cd1c56689a373fab3f63ece'
   >>> ulid.timestamp
   1505945939.153
   >>> ulid.datetime
   datetime.datetime(2017, 9, 20, 22, 18, 59, 153000, tzinfo=datetime.timezone.utc)
   >>> ulid.to_uuid()
   UUID('015ea15f-6cd1-c566-89a3-73fab3f63ece')

.. usage-end


Other implementations
---------------------

* `ahawker/ulid <https://github.com/ahawker/ulid>`_
* `valohai/ulid2 <https://github.com/valohai/ulid2>`_
* `mdipierro/ulid <https://github.com/mdipierro/ulid>`_