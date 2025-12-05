"""
Unittests for optimization module
"""

from pymc_elicito.optimization import run_optimizer


def test_run_optimizer():
    # Just ensure the function runs without errors
    run_optimizer()
