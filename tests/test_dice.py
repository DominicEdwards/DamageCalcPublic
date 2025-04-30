import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import numpy as np

from src.dice import Die


class TestDie:
    def test_roll_basic(self):
        d6 = Die(6)
        rolls = d6.roll(1000)
        assert isinstance(rolls, np.ndarray)
        assert rolls.shape == (1000,)
        assert np.all(rolls >= 1)
        assert np.all(rolls <= 6)

    def test_roll_min_value(self):
        d6 = Die(6, min_value=3)
        rolls = d6.roll(1000)
        assert np.all(rolls >= 3)
        assert np.all(rolls <= 6)

    def test_roll_reroll_below_2(self):
        # reroll any value < 2 (i.e., reroll 1s)
        d6 = Die(6, reroll=2)
        rolls = d6.roll(1000)
        assert np.all(rolls >= 2)
        assert np.all(rolls <= 6)

    def test_roll_reroll_below_2_point_5(self):
        # reroll any value < 2.5 (i.e., reroll 1s and 2s)
        d6 = Die(6, reroll=2.5)
        rolls = d6.roll(1000)
        assert np.all(rolls >= 3)
        assert np.all(rolls <= 6)

    def test_roll_reroll_below_3_max_1(self):
        # reroll any value < 3, but only once per die
        d6 = Die(6, reroll=3, max_rerolls=1)
        rolls = d6.roll(10000)
        # Some rolls may still be 1 or 2 if rerolled value is also < 3
        assert np.all(rolls >= 1)
        assert np.all(rolls <= 6)
        # But the proportion of 1s and 2s should be much lower than 1/3
        low = np.sum(rolls < 3) / 10000
        assert low < 0.2

    def test_parse_reroll_threshold(self):
        d = Die.parse('d6r2')
        assert isinstance(d, Die)
        assert d.sides == 6
        assert d.reroll == 2
        assert d.max_rerolls is None

    def test_parse_reroll_float_threshold(self):
        d = Die.parse('d6r2.5')
        assert isinstance(d, Die)
        assert d.sides == 6
        assert d.reroll == 2.5
        assert d.max_rerolls is None

    def test_parse_reroll_threshold_and_max(self):
        d = Die.parse('d6r2x3')
        assert isinstance(d, Die)
        assert d.sides == 6
        assert d.reroll == 2
        assert d.max_rerolls == 3

    def test_repr(self):
        d8 = Die(8)
        rep = repr(d8)
        assert "Die" in rep and "8" in rep
