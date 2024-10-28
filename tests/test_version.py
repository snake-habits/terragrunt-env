import pytest

from terragrunt_env import version

@pytest.mark.parametrize(
    "test_input,major,minor,patch",
    [
        ("1.0.0", 1, 0, 0)
    ]
)
def test_parts(test_input, major, minor, patch):
    v = version.Version(test_input)
    assert v.major == major
    assert v.minor == minor
    assert v.patch == patch

