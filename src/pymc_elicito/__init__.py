"""
A framework for expert prior elicitation in Python.

Learn prior distributions for parameters in a Bayesian
model based on expert information.
"""

import importlib.metadata

__version__ = importlib.metadata.version("pymc_elicito")

__all__ = ["hello_world"]


def hello_world() -> str:
    """
    Print hello world

    Returns
    -------
    :
        hello world
    """
    return "hello world"
