<h1 align="center">
	<br>
	<br>
	<img width="360" src="logo.png" alt="ulid">
	<br>
	<br>
	<br>
</h1>

[![](https://img.shields.io/pypi/v/python-ulid.svg?style=flat-square)](https://pypi.python.org/pypi/python-ulid)
[![](https://img.shields.io/travis/mdomke/python-ulid/master.svg?style=flat-square)](https://travis-ci.org/mdomke/python-ulid)
[![](https://img.shields.io/pypi/l/python-ulid.svg?style=flat-square)](https://pypi.python.org/pypi/python-ulid)
[![](https://img.shields.io/codecov/c/github/mdomke/python-ulid.svg?style=flat-square)](https://codecov.io/gh/mdomke/python-ulid)
[![](https://readthedocs.org/projects/python-ulid/badge/?version=latest&style=flat-square)](https://python-ulid.readthedocs.io)
[![](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://black.readthedocs.io/en/stable/index.html)

What is this?
=============

This is a port of the original JavaScript [ULID][1] implementation to Python.

A ULID is a *universally unique lexicographically sortable identifier*. It is

- 128-bit compatible with UUID
- 1.21e+24 unique ULIDs per millisecond
- Lexicographically sortable!
- Canonically encoded as a 26 character string, as opposed to the 36 character UUID
- Uses Crockford's base32 for better efficiency and readability (5 bits per character)
- Case insensitive
- No special characters (URL safe)

In general the structure of a ULID is as follows:

```
   01AN4Z07BY      79KA1307SR9X4MV3
  |----------|    |----------------|
   Timestamp          Randomness
     48bits             80bits
```


For more information have a look at the original [specification][2].

Installation
------------

```bash
  $ pip install python-ulid
```

Basic Usage
-----------

Create a new `ULID` on from the current timestamp

```python
  >>> from ulid import ULID
  >>> ulid = ULID()
```

Encode in different formats

```python
  >>> str(ulid)
  '01BTGNYV6HRNK8K8VKZASZCFPE'
  >>> ulid.hex
  '015ea15f6cd1c56689a373fab3f63ece'
  >>> int(ulid)
  1820576928786795198723644692628913870
  >>> ulid.bytes
  b'\x01^\xa1_l\xd1\xc5f\x89\xa3s\xfa\xb3\xf6>\xce'
```

Access timestamp attribute

```python
  >>> ulid.timestamp
  1505945939.153
  >>> ulid.milliseconds
  1505945939153
  >>> ulid.datetime
  datetime.datetime(2017, 9, 20, 22, 18, 59, 153000, tzinfo=datetime.timezone.utc)
```

Convert to `UUID`

```python
  >>> ulid.to_uuid()
  UUID('015ea15f-6cd1-c566-89a3-73fab3f63ece')
```


Other implementations
---------------------

- [ahawker/ulid](https://github.com/ahawker/ulid)
- [valohai/ulid2](https://github.com/valohai/ulid2)
- [mdipierro/ulid](https://github.com/mdipierro/ulid)


[1]: https://github.com/alizain/ulid
[2]: https://github.com/alizain/ulid#specification
