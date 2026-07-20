.. _changelog:

Changelog
=========

Versions follow `Semantic Versioning <http://www.semver.org>`_

`4.0.0`_ - 2026-07-20
---------------------

.. warning::

   **Breaking change:** the ``ValueProvider`` class and the ``ULID.provider`` class attribute
   have been removed. ULID generation is now handled by the new :class:`.ULIDGenerator` together
   with pluggable monotonicity policies. To customize generation, construct a
   :class:`.ULIDGenerator` (optionally with a custom clock, randomness source, or policy) and
   either call its ``generate()`` method or assign it to ``ulid.default_generator``.

Added
~~~~~
* Added a public :class:`.ULIDGenerator` class that encapsulates ULID generation and can be
  configured with a custom clock, randomness source, and monotonicity policy.
* Added pluggable monotonicity policies: :class:`.StrictMonotonicPolicy` (the default),
  :class:`.LaxMonotonicPolicy` and :class:`.PureRandomPolicy`, together with the
  :class:`.MonotonicityPolicy` protocol and the :class:`.BaseMonotonicPolicy` base class for
  implementing custom policies.
* Added a module-level ``ulid.default_generator`` that can be reassigned to route ``ULID()`` and
  the ``ULID.from_*`` constructors through a custom :class:`.ULIDGenerator`.

Removed
~~~~~~~
* Removed the ``ValueProvider`` class and the ``ULID.provider`` attribute in favour of
  :class:`.ULIDGenerator` and the monotonicity policies. Code that replaced ``ULID.provider`` or
  subclassed ``ValueProvider`` must migrate to a custom :class:`.ULIDGenerator` assigned to
  ``ulid.default_generator``.
* Removed the internal ``validate_type`` decorator. The ``ULID.from_*`` constructors still raise
  ``TypeError`` for arguments of the wrong type, so runtime behaviour is unchanged.

`3.2.1`_ - 2026-07-17
---------------------
Fixed
~~~~~
* Corrected the build and publish pipeline and the generated source distribution. This release
  contains no changes to the library code.

`3.2.0`_ - 2026-07-17
---------------------
Added
~~~~~
* Added transparent bidirectional UUIDv7 conversion methods (``ULID.to_uuid7`` and
  ``ULID.from_uuidv7``) `@pirate <https://github.com/pirate>`_.
* Added a ``--uuid7`` option to the CLI's ``show`` command to convert and output a ULID as an
  RFC 4122 compliant UUIDv7.

Changed
~~~~~~~
* Dropped support for Python 3.9 and added support for Python 3.14
  `@Avihais12344 <https://github.com/Avihais12344>`_.
* Depend on ``typing-extensions`` only when running on Python < 3.11 `@musicinmybrain <https://github.com/musicinmybrain>`_.
* Migrated package and development workflow from Hatch to ``uv`` and ``poethepoet``.
* Configured Flox for bootstrapping the development environment.

Fixed
~~~~~
* Fixed a clock-skew bug where non-monotonic ULIDs could be generated when crossing a millisecond boundary between timestamp and randomness sampling `@gaoflow <https://github.com/gaoflow>`_.
* Fixed warning from ``uv`` during synchronization `@jaseemabid <https://github.com/jaseemabid>`_.
* Resolved various Ruff linter warnings and Pyrefly type checker issues.

`3.1.0`_ - 2025-08-18
---------------------
Changed
~~~~~~~
* Added Python 3.13 to the trove classifiers.
* Optimze ``@property`` to ``@cached_property`` `@WH-2099 <https://github.com/WH-2099>`_.
* When generating ULIDs within the same millisecond, the library will ensure monotonic sort order by
  incrementing the randomness component by 1 bit. This process is descrbied in the
  `spec <https://github.com/ulid/spec/blob/master/README.md#monotonicity>`_.

Fixed
~~~~~
* Sharpen regular expression for Pydantic `@aplhk <https://github.com/aplhk>`_.
* Fix Sphinx warnings when referencing ULID from an external project. `@BoboTiG <https://github.com/BoboTiG>`_.

`3.0.0`_ - 2024-10-11
---------------------
Changed
~~~~~~~
* Raise ``TypeError`` instead of ``ValueError`` if constructor is called with value of wrong type.
* Update ``ruff`` linter rules and switch to ``hatch fmt``.

Added
~~~~~
* Added :meth:`.ULID.parse`-method, which allows to create a :class:`.ULID`-instance from an
  arbitrary supported input value. `@perrotuerto <https://github.com/perrotuerto>`_.

Fixed
~~~~~
* Documentation bug in the example of :meth:`.ULID.milliseconds` `@tsugumi-sys <https://github.com/tsugumi-sys>`_.


`2.7.0`_ - 2024-06-17
---------------------
Changed
~~~~~~~
* Ensure that the validation of ULID's timestamp component aligns more closely with
  the ULID specification.

`2.6.0`_ - 2024-05-26
---------------------
Changed
~~~~~~~
* Use stricter validation when a :class:`.ULID` value from user input. When using
  :meth:`.ULID.from_str` we will check if the characters match the base32 alphabet. In general,
  it is ensured that the timestamp part of the ULID is not out of range.

`2.5.0`_ - 2024-04-26
---------------------
Changed
~~~~~~~
* Generate a more accurate JSON schema with Pydantic's ``BaseModel.model_json_schema()``. This
  includes a specification for string and byte representations.

`2.4.0`_ - 2024-04-02
---------------------
Added
~~~~~
* :class:`.ULID` objects are now properly serialized when used as Pydantic types `@Avihais12344 <https://github.com/Avihais12344>`_.


`2.3.0`_ - 2024-03-21
---------------------
Added
~~~~~
* :class:`.ULID` objects can now be converted to bytes with ``bytes(ulid)``.
* The Pydantic v2 protocol is now supported, so that the :class:`.ULID` class can be directly used
  as type annotations in `Pydantic models <https://docs.pydantic.dev/latest/concepts/models/#basic-model-usage>`_

Changed
~~~~~~~
* The type annotations have been adapted, so that the classmethod constructors properly reflect the
  type for :class:`.ULID` subclasses. Thanks to `@johnpaulett <https://github.com/johnpaulett>`_


`2.2.0`_ - 2023-09-21
---------------------
Added
~~~~~
* Added a new flag ``--uuid4`` to the CLI ``show`` command, that converts the provided ``ULID``
  into an RFC 4122 compliant ``UUID``.
* The ``ulid build`` command allows the use of the special value ``-`` for all options to read its
  inputs from ``stdin``. E.g.

  .. code-block:: bash

    $ date --iso-8601 | python -m ulid build --from-datetime -
    01HAT9PVR02T3S13XB48S7GEHE

`2.1.0`_ - 2023-09-21
---------------------
Added
~~~~~
* The new method :meth:`.ULID.to_uuid4` can be used to create an RFC 4122 compliant ``UUID`` from
  an existing :class:`.ULID`.

Changed
~~~~~~~
* The ``validate_types``-decorator that is used for all ``ULID.from_*``-methods to check type
  correctness at runtime has now better support for type hints.
  Thanks to `@johnpaulett <https://github.com/johnpaulett>`_


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

* Make :class:`.ULID`-instances hashable. Thanks to `bendykst <https://github.com/bendykst>`_.
* Added support for Python 3.11.


Changed
~~~~~~~
* Dropped support for Python 3.7 and 3.8.


`1.1.0`_ - 2022-03-10
---------------------
Added
~~~~~
* Added support for Python 3.10.
* Added ``__version__`` variable to package.


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
* The named constructor ``ULID.new`` has been removed. Use one of the specifc named
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

* The ``ULID.str`` and ``ULID.int`` methods have been removed in favour of the more
  Pythonic special dunder-methods. Use ``str(ulid)`` and ``int(ulid)`` instead.
* Added the property :meth:`.ULID.hex` that returns a hex representation of the :class:`.ULID`.

  .. code-block:: python

    >>> ULID().hex
    '0171caa5459a8631a6894d072c8550a8'

* Equality checks and ordering now also work with ``str``-instances.
* The package now has no external dependencies.
* The test-coverage has been raised to 100%.

.. _4.0.0: https://github.com/mdomke/python-ulid/compare/3.2.1...4.0.0
.. _3.2.1: https://github.com/mdomke/python-ulid/compare/3.2.0...3.2.1
.. _3.2.0: https://github.com/mdomke/python-ulid/compare/3.1.0...3.2.0
.. _3.1.0: https://github.com/mdomke/python-ulid/compare/3.0.0...3.1.0
.. _3.0.0: https://github.com/mdomke/python-ulid/compare/2.7.0...3.0.0
.. _2.7.0: https://github.com/mdomke/python-ulid/compare/2.6.0...2.7.0
.. _2.6.0: https://github.com/mdomke/python-ulid/compare/2.5.0...2.6.0
.. _2.5.0: https://github.com/mdomke/python-ulid/compare/2.4.0...2.5.0
.. _2.4.0: https://github.com/mdomke/python-ulid/compare/2.3.0...2.4.0
.. _2.3.0: https://github.com/mdomke/python-ulid/compare/2.2.0...2.3.0
.. _2.2.0: https://github.com/mdomke/python-ulid/compare/2.1.0...2.2.0
.. _2.1.0: https://github.com/mdomke/python-ulid/compare/2.0.0...2.1.0
.. _2.0.0: https://github.com/mdomke/python-ulid/compare/1.1.0...2.0.0
.. _1.1.0: https://github.com/mdomke/python-ulid/compare/1.0.3...1.1.0
.. _1.0.3: https://github.com/mdomke/python-ulid/compare/1.0.2...1.0.3
.. _1.0.0: https://github.com/mdomke/python-ulid/compare/0.2.0...1.0.0

.. _PEP-0561: https://www.python.org/dev/peps/pep-0561/#packaging-type-information
