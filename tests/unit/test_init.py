"""
Unit test for __init__.py
"""

from pymc_elicito import hello_world


def test_hello_world():
    observed = hello_world()
    expected = "hello world"

    assert observed == expected
