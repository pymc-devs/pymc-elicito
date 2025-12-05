"""
Unittests for losses module
"""

import numpy as np
import pytensor.tensor as pt
import pytest
from numpy import testing as npt

from pymc_elicito.losses import MMD2

# assuming k(x, y) = -||x - y||^2
# mean XX: 1/N^2 sum_i sum_j k(x_i, x_j)
# mean YY: 1/N^2 sum_i sum_j k(y_i, y_j)
# mean XY: -2/N^2 sum_i sum_j k(x_i, y_j)


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (
            np.array([[1.0, 2.0], [3.0, 4.0]]),  # x
            np.array([[1.5, 2.5], [3.5, 4.5]]),  # y
            0.5,  # expected MMD^2 value (approx)
        ),
        (
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            0.0,
        ),
        (
            np.array([[0, 4]]),  # mean(XX) = 1/4 (0 - 4 - 4 + 0) = -2
            np.array([[1, 3]]),  # mean(YY) -> 1/4(0 - 2 - 2 + 0) = -1
            # mean(XY) = 1/4(-1 - 3 - 3 - 1) = -2
            1.0,  # xx -2xy + yy = (-2) -2*(-2) + (-1) = 1
        ),
    ],
)
def test_mmd2_call(x, y, expected):
    x_sample = pt.as_tensor_variable(x)
    y_sample = pt.as_tensor_variable(y)

    mmd2 = MMD2(kernel="energy")
    result = mmd2(x_sample, y_sample)

    assert isinstance(result, pt.TensorVariable)
    npt.assert_allclose(result.eval(), expected, atol=1e-4)
