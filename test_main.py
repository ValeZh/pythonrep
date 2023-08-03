import unittest
from unittest.mock import MagicMock, patch, call
import pytest
from main import find_zero_col_in_mass, first_positive_line

TEST_MASS = [[5, -1, -2, -1], [0, 7, 4, 67], [0, 0, 0, 0], [0, 2, 2, 2]]
def test_find_zero_col_in_mass():
    input_pram = TEST_MASS
    actual = find_zero_col_in_mass(input_pram)
    expected = 3
    assert actual == expected

@pytest.mark.parametrize('input_param, expected', [([[5, -1, -2, -1], [0, 7, 4, 67], [0, 0, 0, 0], [0, 2, 2, 2]], 0), ([[-5, -1, -2, -1], [0, -7, -4, -67], [0, 0, 0, 0], [0, -2, -2, -2]], None)])
def test_first_positive_line(input_param, expected):
    actual = first_positive_line(input_param)
    assert actual == expected


if __name__ == '__main__':
    unittest.main()
