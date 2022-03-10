Python ULID
===========

Release v\ |release| (:ref:`What's new <changelog>`)

A :class:`ULID` is a *universally unique lexicographically sortable identifier*. It is

* 128-bit compatible with `UUID`
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


For more information have a look at the original specification_.

Examples
--------

Basic Usage
~~~~~~~~~~~

Create a new :class:`ULID` object from the current timestamp

.. code-block:: python

   >>> from ulid import ULID
   >>> ULID()
   ULID(01E75HZVW36EAZKMF1W7XNMSB4)

or use one of the named constructors 

.. code-block:: python

   >>> import time, datetime
   >>> ULID.from_timestamp(time.time())
   ULID(01E75J1MKKWMGG0N5MBHFMRC84)
   >>> ULID.from_datetime(datetime.datetime.now())
   ULID(01E75J2XBK390V2XRH44EHC10X)

There are several options for encoding the :class:`ULID` object (e.g. string, hex, int),
as well as to access the timestamp attribute in different formats:

.. code-block:: python

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

API documentation
-----------------

.. toctree::
   :maxdepth: 2

   api

.. toctree::
   :maxdepth: 1

   changelog

.. _specification: https://github.com/alizain/ulid#specification
