.. _changelog:

Changelog
=========

Versions follow `Semantic Versioning <http://www.semver.org>`_

`2.0.0`_ - 2023-09-20
---------------------

Added
~~~~~
* New command line interface to easily generate and inspect ULIDs from the terminal

  .. code-block:: bash

    $ ulid build
    01HASJFZZ862S826DA2NJK4WMT

    $ ulid show 01HASJFZZ862S826DA2NJK4WMT
    ULID:      01HASJFZZ862S826DA2NJK4WMT
    Hex:       018ab327ffe830b28119aa156532729a
    Int:       2049398682679492051963931130707735194
    Timestamp: 1695222857.704
    Datetime:  2023-09-20 15:14:17.704000+00:00

  The CLI can also be invoked as a module ``python -m ulid``.
  For more information see ``ulid --help``.

* Make :class:`.ULID`-instances hashable.
* Added support for Python 3.11.


Changed
~~~~~~~
* Dropped support for Python 3.7 and 3.8.


`1.1.0`_ - 2022-03-10
---------------------

Added
~~~~~
* Added support for Python 3.10.
* Added :attr:`__version__` variable to package.


`1.0.3`_ - 2021-07-14
---------------------

Added
~~~~~
* Enable tool based type checking as described in `PEP-0561`_ by adding the ``py.typed`` marker.

Changed
~~~~~~~
* Use GitHub actions instead of Travis.


`1.0.0`_ - 2020-04-30
---------------------

Added
~~~~~
* Added type annotations
* Added the named constructors :meth:`.ULID.from_datetime`, :meth:`.ULID.from_timestamp` and
  :meth:`.ULID.from_hex`.

Changed
~~~~~~~
* Dropped support for Python 2. Only Python 3.6+ is supported.
* The named constructor :meth:`.ULID.new` has been removed. Use one of the specifc named
  constructors instead. For a new :class:`.ULID` created from the current timestamp use the
  standard constructor.

  .. code-block:: python

    # old
    ulid = ULID.new()
    ulid = ULID.new(time.time())
    ulid = ULID.new(datetime.now())

    # new
    ulid = ULID()
    ulid = ULID.from_timestamp(time.time())
    ulid = ULID.from_datetime(datetime.now())

* The :meth:`.ULID.str` and :meth:`.ULID.int` methods have been removed in favour of the more
  Pythonic special dunder-methods. Use `str(ulid)` and `int(ulid)` instead.
* Added the property :meth:`.ULID.hex` that returns a hex representation of the :class:`.ULID`.

  .. code-block:: python

    >>> ULID().hex
    '0171caa5459a8631a6894d072c8550a8'

* Equality checks and ordering now also work with ``str``-instances.
* The package now has no external dependencies.
* The test-coverage has been raised to 100%.

.. _2.0.0: https://github.com/mdomke/python-ulid/compare/1.1.0...2.0.0
.. _1.1.0: https://github.com/mdomke/python-ulid/compare/1.0.3...1.1.0
.. _1.0.3: https://github.com/mdomke/python-ulid/compare/1.0.2...1.0.3
.. _1.0.0: https://github.com/mdomke/python-ulid/compare/0.2.0...1.0.0

.. _PEP-0561: https://www.python.org/dev/peps/pep-0561/#packaging-type-information
