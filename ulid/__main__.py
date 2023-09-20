import argparse
import shutil
import sys
import textwrap
from collections.abc import Sequence
from datetime import datetime
from datetime import timezone
from functools import partial
from uuid import UUID

import ulid
from ulid import ULID


def make_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=textwrap.indent(
            textwrap.dedent(
                """
            Create or inspect ULIDs

            A ULID is a universally unique lexicographically sortable identifier
            with the following structure

               01AN4Z07BY      79KA1307SR9X4MV3
              |----------|    |----------------|
               Timestamp          Randomness
                 48bits             80bits
            """
            ).strip(),
            "    ",
        ),
        formatter_class=partial(
            argparse.RawDescriptionHelpFormatter,
            # Prevent argparse from taking up the entire width of the terminal window
            # which impedes readability.
            width=min(shutil.get_terminal_size().columns - 2, 127),
        ),
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument("--version", "-V", action="version", version=ulid.__version__)

    subparsers = parser.add_subparsers(title="subcommands")
    b = subparsers.add_parser(
        "build",
        help="generate ULIDs from different sources",
    )
    b.add_argument(
        "--from-int",
        type=int,
        metavar="<int>",
        help="create from integer",
    )
    b.add_argument(
        "--from-hex",
        type=str,
        metavar="<str>",
        help="create from 32 character hex value",
    )
    b.add_argument(
        "--from-str",
        type=str,
        metavar="<str>",
        help="create from base32 encoded string of length 26",
    )
    b.add_argument(
        "--from-timestamp",
        type=parse_numeric,
        metavar="<int|float>",
        help="create from timestamp either as float in secs or int as millis",
    )
    b.add_argument(
        "--from-datetime",
        type=datetime.fromisoformat,
        metavar="<iso8601>",
        help="create from datetime. The timestamp part of the ULID will be taken from the datetime",
    )
    b.add_argument(
        "--from-uuid",
        type=UUID,
        metavar="<uuid>",
        help="create from given UUID. The timestamp part will be random.",
    )
    b.set_defaults(func=build)

    s = subparsers.add_parser("show", help="show properties of a ULID")
    s.add_argument("ulid", help="the ULID to inspect. The special value - reads from stdin")
    s.add_argument("--uuid", action="store_true", help="convert to UUID")
    s.add_argument("--hex", action="store_true", help="convert to hex")
    s.add_argument("--int", action="store_true", help="convert to int")
    s.add_argument("--timestamp", "--ts", action="store_true", help="show timestamp")
    s.add_argument("--datetime", "--dt", action="store_true", help="show datetime")
    s.set_defaults(func=show)
    return parser


def parse_numeric(s: str) -> int | float:
    try:
        return int(s)
    except ValueError:
        return float(s)


def main(argv: Sequence[str], prog: str | None = None) -> None:
    args = make_parser(prog).parse_args(argv)
    args.func(args)


def build(args: argparse.Namespace) -> None:
    ulid: ULID
    if args.from_int is not None:
        ulid = ULID.from_int(args.from_int)
    elif args.from_hex is not None:
        ulid = ULID.from_hex(args.from_hex)
    elif args.from_str is not None:
        ulid = ULID.from_str(args.from_str)
    elif args.from_timestamp is not None:
        ulid = ULID.from_timestamp(args.from_timestamp)
    elif args.from_datetime is not None:
        ulid = ULID.from_datetime(args.from_datetime)
    elif args.from_uuid is not None:
        ulid = ULID.from_uuid(args.from_uuid)
    else:
        ulid = ULID.from_datetime(datetime.now(timezone.utc))
    print(ulid)


def show(args: argparse.Namespace) -> None:
    value = sys.stdin.readline().strip() if args.ulid == "-" else args.ulid
    ulid: ULID = ULID.from_str(value)
    if args.uuid:
        print(ulid.to_uuid())
    elif args.hex:
        print(ulid.hex)
    elif args.int:
        print(int(ulid))
    elif args.timestamp:
        print(ulid.timestamp)
    elif args.datetime:
        print(ulid.datetime)
    else:
        print(
            textwrap.dedent(
                f"""
                ULID:      {ulid!s}
                Hex:       {ulid.hex}
                Int:       {int(ulid)}
                Timestamp: {ulid.timestamp}
                Datetime:  {ulid.datetime}
                """
            ).strip()
        )


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], "python -m ulid")
