from ... import units as u

from ..helper import assert_quantity_allclose, pytest


def test_assert_quantity_allclose():

    assert_quantity_allclose([1,2], [1,2])

    assert_quantity_allclose([1,2] * u.m, [100,200] * u.cm)

    assert_quantity_allclose([1,2] * u.m, [101,201] * u.cm, atol=2 * u.cm)

    with pytest.raises(AssertionError):
        assert_quantity_allclose([1,2] * u.m, [90,200] * u.cm)

    with pytest.raises(AssertionError):
        assert_quantity_allclose([1,2] * u.m, [101,201] * u.cm, atol=0.5 * u.cm)

    with pytest.raises(TypeError) as exc:
        assert_quantity_allclose([1,2] * u.m, [100,200])
    assert exc.value.args[0] == "If `actual` is a Quantity, `desired` should also be a Quantity"

    with pytest.raises(TypeError) as exc:
        assert_quantity_allclose([1,2], [100,200] * u.cm)
    assert exc.value.args[0] == "If `desired` is a Quantity, `actual` should also be a Quantity"

    with pytest.raises(TypeError) as exc:
        assert_quantity_allclose([1,2] * u.m, [100,200] * u.cm, atol=0.3)
    assert exc.value.args[0] == "If `actual` and `desired` are Quantities, `atol` parameter should also be a Quantity"

    with pytest.raises(TypeError) as exc:
        assert_quantity_allclose([1,2], [1, 2], atol=0.3 * u.m)
    assert exc.value.args[0] == "If `actual` and `desired` are not Quantities, `atol` parameter should also not be a Quantity"

