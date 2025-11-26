import pytest
from app.utils import normalize_email, safe_div

def test_normalize_email():
    assert normalize_email("mchen@findoctave.com") == "mchen@findoctave.com"
    assert normalize_email("mChEN@fin docTave.com") == "mchen@findoctave.com"
    assert normalize_email("mChEN@fin doc ave.com") != "mchen@findoctave.com"
    with pytest.raises(TypeError):
        normalize_email(10)

def test_safe_div():
    assert safe_div(10, 2) == 5
    assert safe_div(10, 0) is None
    assert safe_div(-10, 2) == -5

@pytest.mark.parametrize(
"a,b,expected",
    [
    (10, 2, 5),
    (5, -1, -5),
    (3, 0, None),
    ],
)

def test_safe_div_param(a, b, expected):
    assert safe_div(a, b) == expected