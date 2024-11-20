import pytest

from terragrunt_env import version


@pytest.mark.parametrize(
    "test_input,major,minor,patch",
    [("1.0.0", 1, 0, 0), ("1.2.3", 1, 2, 3), ("99.100.101", 99, 100, 101)],
)
def test_parts(test_input, major, minor, patch):
    v = version.Version(test_input)
    assert v.major == major
    assert v.minor == minor
    assert v.patch == patch


@pytest.mark.parametrize(
    "test_input", ["v-1", "v1.-2", "v1.2.-3", "v1.-2.3", "1.2.3-dev1-pre2"]
)
def test_invalid_version(test_input):
    with pytest.raises(version.InvalidVersion):
        version.Version(test_input)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", None),
        ("1.2.3-pre1", ("rc", 1)),
        ("1.2.3-rev2", None),
        ("1.2.3-dev3", None),
        ("1.2.3-pre1-rev2", ("rc", 1)),
        ("1.2.3-pre1-dev3", ("rc", 1)),
        ("1.2.3-rev2-dev3", None),
        ("1.2.3-pre1-rev2-dev3", ("rc", 1)),
        ("1.2.3-alpha1", ("a", 1)),
        ("1.2.3-a1", ("a", 1)),
        ("1.2.3-beta2", ("b", 2)),
        ("1.2.3-b2", ("b", 2)),
        ("1.2.3-c3", ("rc", 3)),
        ("1.2.3-preview3", ("rc", 3)),
        ("1.2.3-rc3", ("rc", 3)),
    ],
)
def test_pre_value(test_input, expected):
    v = version.Version(test_input)
    assert v.pre == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", None),
        ("1.2.3-pre1", None),
        ("1.2.3-rev2", 2),
        ("1.2.3-dev3", None),
        ("1.2.3-pre1-rev2", 2),
        ("1.2.3-pre1-dev3", None),
        ("1.2.3-rev2-dev3", 2),
        ("1.2.3-pre1-rev2-dev3", 2),
        ("1.2.3-r1", 1),
        ("1.2.3-post2", 2),
    ],
)
def test_post_value(test_input, expected):
    v = version.Version(test_input)
    assert v.post == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", None),
        ("1.2.3-pre1", None),
        ("1.2.3-rev2", None),
        ("1.2.3-dev3", 3),
        ("1.2.3-pre1-rev2", None),
        ("1.2.3-pre1-dev3", 3),
        ("1.2.3-rev2-dev3", 3),
        ("1.2.3-pre1-rev2-dev3", 3),
    ],
)
def test_dev_value(test_input, expected):
    v = version.Version(test_input)
    assert v.dev == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", False),
        ("1.2.3-pre1", False),
        ("1.2.3-rev2", True),
        ("1.2.3-dev3", False),
        ("1.2.3-pre1-rev2", True),
        ("1.2.3-pre1-dev3", False),
        ("1.2.3-rev2-dev3", True),
        ("1.2.3-pre1-rev2-dev3", True),
    ],
)
def test_is_postrelease(test_input, expected):
    v = version.Version(test_input)
    assert v.is_postrelease == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", False),
        ("1.2.3-pre1", False),
        ("1.2.3-rev2", False),
        ("1.2.3-dev3", True),
        ("1.2.3-pre1-rev2", False),
        ("1.2.3-pre1-dev3", True),
        ("1.2.3-rev2-dev3", True),
        ("1.2.3-pre1-rev2-dev3", True),
    ],
)
def test_is_devrelease(test_input, expected):
    v = version.Version(test_input)
    assert v.is_devrelease == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", False),
        ("1.2.3-pre1", True),
        ("1.2.3-rev2", False),
        ("1.2.3-dev3", True),
        ("1.2.3-pre1-rev2", True),
        ("1.2.3-pre1-dev3", True),
        ("1.2.3-rev2-dev3", True),
        ("1.2.3-pre1-rev2-dev3", True),
    ],
)
def test_is_prerelease(test_input, expected):
    v = version.Version(test_input)
    assert v.is_prerelease == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1.2.3", "1.2.3"),
        ("1.2.3-pre1", "1.2.3rc1"),
        ("1.2.3-rev2", "1.2.3"),
        ("1.2.3-dev3", "1.2.3"),
        ("1.2.3-pre1-rev2", "1.2.3rc1"),
        ("1.2.3-pre1-dev3", "1.2.3rc1"),
        ("1.2.3-rev2-dev3", "1.2.3"),
        ("1.2.3-pre1-rev2-dev3", "1.2.3rc1"),
        ("1.2.3-alpha1", "1.2.3a1"),
        ("1.2.3-a1", "1.2.3a1"),
        ("1.2.3-beta2", "1.2.3b2"),
        ("1.2.3-b2", "1.2.3b2"),
        ("1.2.3-c3", "1.2.3rc3"),
        ("1.2.3-preview3", "1.2.3rc3"),
        ("1.2.3-rc3", "1.2.3rc3"),
    ],
)
def test_str(test_input, expected):
    v = version.Version(test_input)
    assert str(v) == expected


@pytest.mark.parametrize(
    "version1,version2,expected",
    [
        ("1.2.3", "1.2.3", False),
        ("1.2.3", "v1.2.3", False),
        ("1.2.2", "1.2.3", True),
        ("1.1.3", "1.2.3", True),
        ("0.2.3", "1.2.3", True),
        ("1.2.3-a1", "1.2.3", True),
        ("1.2.3-b2", "1.2.3", True),
        ("1.2.3-c3", "1.2.3", True),
        ("1.2.3-pre4", "1.2.3", True),
        ("1.2.3-r5", "1.2.3", False),
        ("1.2.3-dev6", "1.2.3", True),
        ("1.2.3", "1.2.3-a1", False),
        ("1.2.3", "1.2.3-b2", False),
        ("1.2.3", "1.2.3-c3", False),
        ("1.2.3", "1.2.3-pre4", False),
        ("1.2.3", "1.2.3-r5", True),
        ("1.2.3", "1.2.3-dev6", False),
    ],
)
def test_less_then(version1, version2, expected):
    v1 = version.Version(version1)
    v2 = version.Version(version2)
    assert (v1 < v2) is expected


@pytest.mark.parametrize(
    "version1,version2,expected",
    [
        ("1.2.3", "1.2.3", True),
        ("1.2.3", "v1.2.3", True),
        ("1.2.2", "1.2.3", True),
        ("1.1.3", "1.2.3", True),
        ("0.2.3", "1.2.3", True),
        ("1.2.3-a1", "1.2.3", True),
        ("1.2.3-b2", "1.2.3", True),
        ("1.2.3-c3", "1.2.3", True),
        ("1.2.3-pre4", "1.2.3", True),
        ("1.2.3-r5", "1.2.3", False),
        ("1.2.3-dev6", "1.2.3", True),
        ("1.2.3", "1.2.3-a1", False),
        ("1.2.3", "1.2.3-b2", False),
        ("1.2.3", "1.2.3-c3", False),
        ("1.2.3", "1.2.3-pre4", False),
        ("1.2.3", "1.2.3-r5", True),
        ("1.2.3", "1.2.3-dev6", False),
    ],
)
def test_less_then_or_equal(version1, version2, expected):
    v1 = version.Version(version1)
    v2 = version.Version(version2)
    assert (v1 <= v2) is expected


@pytest.mark.parametrize(
    "version1,version2,expected",
    [
        ("1.2.3", "1.2.3", False),
        ("1.2.3", "v1.2.3", False),
        ("1.2.2", "1.2.3", False),
        ("1.1.3", "1.2.3", False),
        ("0.2.3", "1.2.3", False),
        ("1.2.3-a1", "1.2.3", False),
        ("1.2.3-b2", "1.2.3", False),
        ("1.2.3-c3", "1.2.3", False),
        ("1.2.3-pre4", "1.2.3", False),
        ("1.2.3-r5", "1.2.3", True),
        ("1.2.3-dev6", "1.2.3", False),
        ("1.2.3", "1.2.3-a1", True),
        ("1.2.3", "1.2.3-b2", True),
        ("1.2.3", "1.2.3-c3", True),
        ("1.2.3", "1.2.3-pre4", True),
        ("1.2.3", "1.2.3-r5", False),
        ("1.2.3", "1.2.3-dev6", True),
    ],
)
def test_greater_then(version1, version2, expected):
    v1 = version.Version(version1)
    v2 = version.Version(version2)
    assert (v1 > v2) is expected


@pytest.mark.parametrize(
    "version1,version2,expected",
    [
        ("1.2.3", "1.2.3", True),
        ("1.2.3", "v1.2.3", True),
        ("1.2.2", "1.2.3", False),
        ("1.1.3", "1.2.3", False),
        ("0.2.3", "1.2.3", False),
        ("1.2.3-a1", "1.2.3", False),
        ("1.2.3-b2", "1.2.3", False),
        ("1.2.3-c3", "1.2.3", False),
        ("1.2.3-pre4", "1.2.3", False),
        ("1.2.3-r5", "1.2.3", True),
        ("1.2.3-dev6", "1.2.3", False),
        ("1.2.3", "1.2.3-a1", True),
        ("1.2.3", "1.2.3-b2", True),
        ("1.2.3", "1.2.3-c3", True),
        ("1.2.3", "1.2.3-pre4", True),
        ("1.2.3", "1.2.3-r5", False),
        ("1.2.3", "1.2.3-dev6", True),
    ],
)
def test_greater_then_or_equal(version1, version2, expected):
    v1 = version.Version(version1)
    v2 = version.Version(version2)
    assert (v1 >= v2) is expected


@pytest.mark.parametrize(
    "version1,version2,expected",
    [
        ("1.2.3", "1.2.3", True),
        ("1.2.3", "v1.2.3", True),
        ("1.2.3-a1", "1.2.3-alpha1", True),
        ("1.2.3-b2", "1.2.3-beta2", True),
        ("1.2.3-c3", "1.2.3-pre3", True),
        ("1.2.3-c3", "1.2.3-preview3", True),
        ("1.2.3-c3", "1.2.3-rc3", True),
        ("1.2.3-pre3", "1.2.3-c3", True),
        ("1.2.3-pre3", "1.2.3-preview3", True),
        ("1.2.3-pre3", "1.2.3-rc3", True),
        ("1.2.3-preview3", "1.2.3-c3", True),
        ("1.2.3-preview3", "1.2.3-pre3", True),
        ("1.2.3-preview3", "1.2.3-rc3", True),
        ("1.2.3-rev4", "1.2.3-r4", True),
        ("1.2.3-rev4", "1.2.3-post4", True),
        ("1.2.3-r4", "1.2.3-rev4", True),
        ("1.2.3-r4", "1.2.3-post4", True),
        ("1.2.3-post4", "1.2.3-rev4", True),
        ("1.2.3-post4", "1.2.3-r4", True),
        ("1.2.3-a1", "1.2.3-b1", False),
        ("1.2.3-a1", "1.2.3-c1", False),
        ("1.2.3-b1", "1.2.3-c1", False),
        ("1.2.3-a", "1.2.3-a0", True),
        ("1.2.3-99", "1.2.3-post99", True),
    ],
)
def test_equals(version1, version2, expected):
    v1 = version.Version(version1)
    v2 = version.Version(version2)
    assert (v1 == v2) is expected


@pytest.mark.parametrize(
    "version1,version2,expected",
    [
        ("1.2.3", "1.2.3", False),
        ("1.2.3", "v1.2.3", False),
    ],
)
def test_not_equals(version1, version2, expected):
    v1 = version.Version(version1)
    v2 = version.Version(version2)
    assert (v1 != v2) is expected
