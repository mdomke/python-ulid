.. begin-html-header

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
         <img src="https://img.shields.io/github/actions/workflow/status/mdomke/python-ulid/lint-and-test.yml?style=flat-square&brach=main" />
      </a>
      <a href="https://python-ulid.readthedocs.io">
         <img src="https://readthedocs.org/projects/python-ulid/badge/?version=latest&style=flat-square" />
      </a>
      <a href="https://black.readthedocs.io/en/stable/index.html">
         <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" />
      </a>
   </p>

.. end-html-header

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

to include Pydantic support install the optional dependency like so

.. code-block:: bash

  $ pip install python-ulid[pydantic]

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

There are several options for encoding the ``ULID`` object
(e.g. string, hex, int, bytes, UUID):

.. code-block:: pycon

   >>> str(ulid)
   '01BTGNYV6HRNK8K8VKZASZCFPE'
   >>> ulid.hex
   '015ea15f6cd1c56689a373fab3f63ece'
   >>> int(ulid)
   1820576928786795198723644692628913870
   >>> bytes(ulid)
   b'\x01^\xa1_l\xd1\xc5f\x89\xa3s\xfa\xb3\xf6>\xce'
   >>> ulid.to_uuid()
   UUID('015ea15f-6cd1-c566-89a3-73fab3f63ece')

It is also possible to directly access the timestamp component of a ``ULID``,
either in UNIX epoch or as ``datetime.datetime``

.. code-block:: pycon

   >>> ulid.timestamp
   1505945939.153
   >>> ulid.datetime
   datetime.datetime(2017, 9, 20, 22, 18, 59, 153000, tzinfo=datetime.timezone.utc)

.. usage-end

.. pydantic-begin

Pydantic integration
---------------------

The ``ULID`` class can be directly used for the popular data validation library
`Pydantic <https://docs.pydantic.dev/latest/>`_ like so

.. code-block:: python

  from pydantic import BaseModel
  from ulid import ULID


  class Model(BaseModel):
    ulid: ULID

  model = Model(ulid="DX89370400440532013000")  # OK
  model = Model(ulid="not-a-ulid")  # Raises ValidationError

.. pydantic-end

.. cli-begin

Command line interface
-----------------------

The package comes with a CLI interface that can be invoked either by the script name
``ulid`` or as python module ``python -m ulid``. The CLI allows you to generate, inspect
and convert ULIDs, e.g.

.. code-block:: bash

   $ ulid build
   01HASFKBN8SKZTSVVS03K5AMMS

   $ ulid build --from-datetime=2023-09-23T10:20:30
   01HB0J0F5GCKEXNSWVAD5PEAC1

   $ ulid show 01HASFKBN8SKZTSVVS03K5AMMS
   ULID:      01HASFKBN8SKZTSVVS03K5AMMS
   Hex:       018ab2f9aea8ccffacef7900e6555299
   Int:       2049395013039097460549394558635823769
   Timestamp: 1695219822.248
   Datetime:  2023-09-20 14:23:42.248000+00:00

There are several flags to select specific output formats for the ``show`` command, e.g.


.. code-block:: bash

   $ ulid show --datetime 01HASFKBN8SKZTSVVS03K5AMMS
   2023-09-20 14:23:42.248000+00:00

The special character ``-`` allows to read values from ``stdin`` so that they can be piped. E.g.

.. code-block:: bash

   $ echo 01HASFKBN8SKZTSVVS03K5AMMS | ulid show --uuid -
   018ab2f9-aea8-4cff-acef-7900e6555299

   $ date --iso-8601 | python -m ulid build --from-datetime -
   01HAT9PVR02T3S13XB48S7GEHE

For a full overview of flags for the ``build`` and ``show`` commands use the ``--help`` option
(e.g. ``ulid show --help``).

.. cli-end

Other implementations
---------------------

* `ahawker/ulid <https://github.com/ahawker/ulid>`_
* `valohai/ulid2 <https://github.com/valohai/ulid2>`_
* `mdipierro/ulid <https://github.com/mdipierro/ulid>`_
* `oklog/ulid <https://github.com/oklog/ulid>`_
* `ulid/javascript <https://github.com/ulid/javascript>`_
* `RobThree/NUlid <https://github.com/RobThree/NUlid>`_
* `imdario/go-ulid <https://github.com/imdario/go-ulid>`_
