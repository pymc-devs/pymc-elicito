"""
Loss functions

Computing discrepancy between expert summaries and model simulations
"""

from enum import Enum
from typing import Any, Union

import pytensor.tensor as pt


class Kernel(str, Enum):
    """Suppoted kernel types for MMD loss"""

    ENERGY = "energy"
    GAUSSIAN = "gaussian"


class MMD2:
    """
    Maximum mean discrepancy loss
    """

    def __init__(
        self, kernel: Union[Kernel, str] = Kernel.ENERGY, **kwargs: dict[Any, Any]
    ) -> None:
        """
        Compute the biased, squared maximum mean discrepancy

        Parameters
        ----------
        kernel :
            Kernel type used for computing the MMD.
            Currently supported: "energy", "gaussian".

        **kwargs :
            additional keyword arguments that might be required by the
            different individual kernels
        """
        # ensure that all additionally, required arguments are provided for
        # the respective kernel
        try:
            self.kernel_type = Kernel(kernel)
        except ValueError:
            raise ValueError(  # noqa: TRY003
                f"Invalid kernel '{kernel}'. "
                f"Must be one of: {[k.value for k in Kernel]}"
            )

        # ensure correct kernel specification
        if self.kernel_type == Kernel.GAUSSIAN:
            if "sigma" not in kwargs:
                raise ValueError(  # noqa: TRY003
                    "You need to pass a 'sigma' argument when using a "
                    "Gaussian kernel."
                )
            self.sigma = kwargs["sigma"]

        self.kernel_name = kernel

    def __call__(
        self,
        x: pt.TensorVariable,  # shape: [B, num_stats]
        y: pt.TensorVariable,  # shape: [B, num_stats]
    ) -> pt.TensorVariable:  # shape: []
        """
        Compute the biased, squared maximum mean discrepancy of two samples

        Returns
        -------
        MMD2_mean :
            Average biased, squared maximum mean discrepancy.
        """
        # treat samples as column vectors [B, num_stats, 1]
        # equivalent to tf.expand_dims(x, -1)
        x = x.dimshuffle(0, 1, "x")
        y = y.dimshuffle(0, 1, "x")

        # compute dot product between samples
        # equivalent to tf.matmul(x, x, transpose_b=True)
        # Input x is (B, N, 1), x.transpose is (B, 1, N) -> Result (B, N, N)
        xx = pt.batched_dot(x, x.transpose(0, 2, 1))
        xy = pt.batched_dot(x, y.transpose(0, 2, 1))
        yy = pt.batched_dot(y, y.transpose(0, 2, 1))

        # compute squared difference
        # We need to reshape diagonals for broadcasting:
        # diag returns (B, N). dimshuffle(0, 1, 'x') makes it (B, N, 1)
        # dimshuffle(0, 'x', 1) makes it (B, 1, N)
        diag_xx = pt.diagonal(xx, axis1=1, axis2=2)
        diag_yy = pt.diagonal(yy, axis1=1, axis2=2)

        u_xx = diag_xx.dimshuffle(0, 1, "x") - 2 * xx + diag_xx.dimshuffle(0, "x", 1)
        u_xy = diag_xx.dimshuffle(0, 1, "x") - 2 * xy + diag_yy.dimshuffle(0, "x", 1)
        u_yy = diag_yy.dimshuffle(0, 1, "x") - 2 * yy + diag_yy.dimshuffle(0, "x", 1)

        # apply kernel function to squared difference
        XX = self.kernel_fun(u_xx)
        XY = self.kernel_fun(u_xy)
        YY = self.kernel_fun(u_yy)

        # compute biased, squared MMD
        # reduce_mean over axes 1 and 2
        mmd2_val = pt.mean(XX, axis=(1, 2))
        mmd2_val -= 2 * pt.mean(XY, axis=(1, 2))
        mmd2_val += pt.mean(YY, axis=(1, 2))

        # Final mean over the batch
        MMD2_mean = pt.mean(mmd2_val)

        return MMD2_mean

    def kernel_fun(self, u: pt.TensorVariable) -> pt.TensorVariable:
        """
        Kernel used in MMD to compute discrepancy between samples.
        """
        if self.kernel_type == Kernel.ENERGY:
            # clipping for numerical stability reasons
            d = -pt.sqrt(pt.clip(u, 1e-8, int(1e10)))
        elif self.kernel_type == Kernel.GAUSSIAN:
            d = pt.exp(-0.5 * (u / self.sigma))
        else:
            # Fallback (should be caught in init)
            d = u

        return d
