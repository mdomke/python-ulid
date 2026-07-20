.. _api:

Developer Interface
===================

.. module:: ulid


ULID
----

.. autoclass:: ULID
   :members:


Generators
----------

Every :class:`ULID` is produced by a :class:`ULIDGenerator`. The bare :class:`ULID` constructor
and the ``ULID.from_*`` factory methods delegate to a shared module-level
:data:`default_generator`. Create your own :class:`ULIDGenerator` to customize the clock, the
randomness source, or the :class:`MonotonicityPolicy`.

.. autoclass:: ULIDGenerator
   :members:

.. autodata:: default_generator
   :no-value:


Monotonicity policies
---------------------

A monotonicity policy decides how the randomness component is resolved when several ULIDs are
generated within the same millisecond. Pass an instance to :class:`ULIDGenerator`. Any object
satisfying the :class:`MonotonicityPolicy` protocol can be used; stateful policies can subclass
:class:`BaseMonotonicPolicy` and only implement the overflow behaviour.

.. autoclass:: MonotonicityPolicy
   :members:

.. autoclass:: BaseMonotonicPolicy
   :members:

.. autoclass:: StrictMonotonicPolicy
   :members:

.. autoclass:: LaxMonotonicPolicy
   :members:

.. autoclass:: PureRandomPolicy
   :members:
