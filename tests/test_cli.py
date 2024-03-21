import pytest

import ulid.__main__ as cli
from ulid import ULID


@pytest.mark.parametrize("option", ["", "uuid", "uuid4", "hex", "int", "timestamp", "datetime"])
def test_parse_show(option: str):
    ulid = ULID()
    argv = ["show", f"--{option}", str(ulid)]
    output = cli.main(argv)
    if option == "uuid":
        assert output == str(ulid.to_uuid())
    elif option == "uuid4":
        assert output == str(ulid.to_uuid4())
    elif option == "hex":
        assert output == ulid.hex
    elif option == "int":
        assert output == str(int(ulid))
    elif option == "timestamp":
        assert output == str(ulid.timestamp)
    elif option == "datetime":
        assert output == ulid.datetime.isoformat()
    else:
        assert str(ulid) in output
        assert ulid.hex in output
        assert str(int(ulid)) in output
        assert str(ulid.timestamp) in output
        assert str(ulid.datetime.isoformat()) in output


@pytest.mark.parametrize(
    "option",
    [
        "",
        "from-uuid",
        "from-str",
        "from-hex",
        "from-int",
        "from-timestamp",
        "from-datetime",
    ],
)
def test_build(option: str):
    ulid = ULID()
    value: str
    includes_randomness = True
    includes_timestamp = True
    if option.endswith("uuid"):
        value = str(ulid.to_uuid())
    elif option.endswith("str"):
        value = str(ulid)
    elif option.endswith("hex"):
        value = ulid.hex
    elif option.endswith("int"):
        value = str(int(ulid))
    elif option.endswith("timestamp"):
        value = str(ulid.timestamp)
        includes_randomness = False
    elif option.endswith("datetime"):
        value = ulid.datetime.isoformat()
        includes_randomness = False
    else:
        includes_timestamp = False
        includes_randomness = False

    argv = ["build"]
    if option:
        argv += [f"--{option}", value]
    output = cli.main(argv)

    if includes_randomness and includes_timestamp:
        assert output == str(ulid)

    ulid_out = ULID.from_str(output)
    if includes_timestamp:
        assert ulid_out.datetime == ulid.datetime
