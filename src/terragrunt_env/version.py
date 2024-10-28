import itertools
import re
from typing import Callable, NamedTuple, SupportsInt, Tuple

from ._structures import InfinityType, NegativeInfinity, PositiveInfinity

_VERSION_PATTERN = r"""
    v?
    (?:
        (?P<release>[0-9]+(?:\.[0-9]+)*)
        (?P<pre>
            [-_\.]?
            (?P<pre_label>alpha|a|beta|b|preview|pre|c|rc)
            [-_\.]?
            (?P<pre_number>[0-9]+)?
        )?
        (?P<post>
            (?:-(?P<post_number1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_label>post|rev|r)
                [-_\.]?
                (?P<post_number2>[0-9]+)?
            )
        )?
        (?P<dev>
            [-_\.]?
            (?P<dev_label>dev)
            [-_\.]?
            (?P<dev_number>[0-9]+)?
        )?
    )
"""

CmpPrePostDevType = InfinityType | Tuple[str, int]
CmpKey = Tuple[Tuple[int, ...], CmpPrePostDevType, CmpPrePostDevType, CmpPrePostDevType]
VersionComparisonMethod = Callable[[CmpKey, CmpKey], bool]


class _Version(NamedTuple):
    release: Tuple[int, ...]
    pre: Tuple[str, int] | None
    post: Tuple[str, int] | None
    dev: Tuple[str, int] | None


class InvalidVersion(ValueError):
    pass


class Version:
    _key: CmpKey
    _regex = re.compile(
        r"^\s*" + _VERSION_PATTERN + r"\s*$", re.VERBOSE | re.IGNORECASE
    )

    def __init__(self, version: str) -> None:
        match = self._regex.search(version)
        if not match:
            raise InvalidVersion(f"Invalid version: '{version}'")

        self._version = _Version(
            release=tuple(int(i) for i in match.group("release").split(".")),
            pre=_parse_label_version(
                match.group("pre_label"), match.group("pre_number")
            ),
            post=_parse_label_version(
                match.group("post_label"),
                match.group("post_number1") or match.group("post_number2"),
            ),
            dev=_parse_label_version(
                match.group("dev_label"), match.group("dev_number")
            ),
        )

        self._key = _cmpkey(
            self._version.release,
            self._version.pre,
            self._version.post,
            self._version.dev,
        )

    def __hash__(self) -> int:
        return hash(self._key)

    def __repr__(self) -> str:
        return f"<Version('{self}')>"

    def __str__(self) -> str:
        parts = [".".join(str(x) for x in self.release)]

        if self.pre is not None:
            parts.append("".join(str(x) for x in self.pre))

        return "".join(parts)

    def __lt__(self, other: object) -> bool:
        return self._key < other._key

    def __le__(self, other: object) -> bool:
        return self._key <= other._key

    def __eq__(self, other: object) -> bool:
        return self._key == other._key

    def __gt__(self, other: object) -> bool:
        return self._key > other._key

    def __ge__(self, other: object) -> bool:
        return self._key >= other._key

    def __ne__(self, other: object) -> bool:
        return self._key != other._key

    @property
    def release(self) -> Tuple[int, ...]:
        return self._version.release

    @property
    def pre(self) -> Tuple[str, int] | None:
        return self._version.pre

    @property
    def post(self) -> int | None:
        return self._version.post[1] if self._version.post else None

    @property
    def dev(self) -> int | None:
        return self._version.dev[1] if self._version.dev else None

    @property
    def is_prerelease(self) -> bool:
        return self.dev is not None or self.pre is not None

    @property
    def is_postrelease(self) -> bool:
        return self.post is not None

    @property
    def is_devrelease(self) -> bool:
        return self.dev is not None

    @property
    def major(self) -> int:
        return self.release[0] if len(self.release) >= 1 else 0

    @property
    def minor(self) -> int:
        return self.release[1] if len(self.release) >= 2 else 0

    @property
    def patch(self) -> int:
        return self.release[2] if len(self.release) >= 3 else 0


def _parse_label_version(
    label: str | None, number: str | bytes | SupportsInt | None
) -> tuple[str, int] | None:
    if label:
        if number is None:
            number = 0

        label = label.lower()
        if label == "alpha":
            label = "a"
        elif label == "beta":
            label = "b"
        elif label in ["c", "pre", "preview"]:
            label = "rc"
        elif label in ["rev", "r"]:
            label = "post"

        return label, int(number)

    if not label and number:
        return "post", int(number)

    return None


def _cmpkey(
    release: Tuple[int, ...],
    pre: Tuple[str, int] | None,
    post: Tuple[str, int] | None,
    dev: Tuple[str, int] | None,
) -> CmpKey:
    _release = tuple(
        reversed(list(itertools.dropwhile(lambda x: x == 0, reversed(release))))
    )

    if pre is None and post is None and dev is not None:
        _pre = NegativeInfinity
    elif pre is None:
        _pre = PositiveInfinity
    else:
        _pre = pre

    if post is None:
        _post = NegativeInfinity
    else:
        _post = post

    if dev is None:
        _dev = PositiveInfinity
    else:
        _dev = dev

    return _release, _pre, _post, _dev
