from typing import List, Optional, Union

import numpy as np
from enum import Enum


class RerollType(Enum):
    NONE = "none"
    LESS_THAN = "less_than"
    SPECIFIC_VALUES = "specific_values"


class Die:
    def __init__(
        self,
        sides: int,
        min_value: Optional[int] = None,
        reroll: Optional[Union[float, List[int]]] = None,
        max_rerolls: Optional[int] = None,
    ):
        if sides < 1:
            raise ValueError("A die must have at least one side.")
        if min_value is not None and min_value > sides:
            raise ValueError("min_value cannot be greater than the number of sides.")
        self.sides = sides
        self.min_value = min_value
        self.reroll = reroll
        self.max_rerolls = max_rerolls

    def roll(self, n: int = 1) -> np.ndarray:
        """
        Roll this die n times and return the results as a numpy array.
        If min_value is set, any result less than min_value is set to min_value
        (e.g., for Great Weapon Fighting).
        If reroll is set (float or int): reroll any result(s) strictly less than reroll until a
        non-reroll value is rolled or until max_rerolls is reached.
        """
        # Fast path: no reroll, no min_value
        if self.reroll is None and self.min_value is None:
            return np.random.randint(1, self.sides + 1, size=n)
        # Fast path: only min_value
        if self.reroll is None and self.min_value is not None:
            rolls = np.random.randint(1, self.sides + 1, size=n)
            return np.where(rolls < self.min_value, self.min_value, rolls)
        # Otherwise, use full logic
        rolls = np.random.randint(1, self.sides + 1, size=n)
        if self.reroll is not None:
            reroll_counts = np.zeros(n, dtype=int)
            reroll_mask = rolls < self.reroll
            while np.any(reroll_mask):
                if self.max_rerolls is not None:
                    reroll_mask = np.logical_and(reroll_mask, reroll_counts < self.max_rerolls)
                if not np.any(reroll_mask):
                    break
                new_rolls = np.random.randint(1, self.sides + 1, size=np.sum(reroll_mask))
                rolls[reroll_mask] = new_rolls
                reroll_counts[reroll_mask] += 1
                reroll_mask = rolls < self.reroll
        if self.min_value is not None:
            rolls = np.where(rolls < self.min_value, self.min_value, rolls)
        return rolls

    @staticmethod
    def parse(die_str: str):
        """
        Parse a die string (e.g., '2d6+3', 'd8', '3d4-1', 'd10min2', 'd10min2+1', 'd10+1min2', 'd6r1', 'd8r1x2', 'd6r1.5x2') into a Die or Roll object.
        Supported:
          - NdX+M (e.g., 2d6+3)
          - dX (e.g., d8)
          - minY (e.g., d8min2)
          - rZ (reroll threshold, e.g., d6r1.5)
          - rZxN (reroll threshold, max N rerolls, e.g., d6r1.5x2)
          - +M before or after minY (e.g., d10+1min2, d10min2+1)
        """
        import re
        from typing import Match
        die_str = die_str.strip().lower()
        # Pattern: [num_dice]d[sides][+/-modifier][minY][+/-modifier][rZ][xN]
        # Accepts modifier before or after minY
        pattern = re.compile(
            r"^(?P<num>\d*)d(?P<sides>\d+)(?P<mod1>[+-]\d+)?(?:min(?P<min>\d+))?(?P<mod2>[+-]\d+)?(?:r(?P<reroll>\d*\.?\d+))?(?:x(?P<maxreroll>\d+))?$"
        )
        match: Match = pattern.match(die_str)
        if match:
            num = int(match.group('num')) if match.group('num') else 1
            sides = int(match.group('sides'))
            mod1 = int(match.group('mod1')) if match.group('mod1') else 0
            min_value = int(match.group('min')) if match.group('min') else None
            mod2 = int(match.group('mod2')) if match.group('mod2') else 0
            mod = mod1 + mod2
            reroll = float(match.group('reroll')) if match.group('reroll') else None
            max_rerolls = int(match.group('maxreroll')) if match.group('maxreroll') else None
            dice = [Die(sides, min_value=min_value, reroll=reroll, max_rerolls=max_rerolls) for _ in range(num)]
            if num == 1 and mod == 0:
                return dice[0]
            else:
                return Roll(dice, modifier=mod)
        # Fallback: just a number (e.g., '8' means d8)
        if die_str.isdigit():
            return Die(int(die_str))
        raise ValueError(f"Invalid die string: {die_str}")

    def __repr__(self):
        args = [str(self.sides)]
        if self.min_value is not None:
            args.append(f"min_value={self.min_value}")
        if self.reroll is not None:
            args.append(f"reroll={self.reroll}")
        if self.max_rerolls is not None:
            args.append(f"max_rerolls={self.max_rerolls}")
        return f"Die({', '.join(args)})"

    def __str__(self):
        return self.__repr__()


class Roll:
    def __init__(self, dice: List[Die], modifier: int = 0):
        if not dice:
            raise ValueError("At least one die is required.")
        self.dice = dice
        self.modifier = modifier

    def roll(self, n_simulations: int = 1) -> np.ndarray:
        """
        Roll all dice in the pool n_simulations times, sum the results, and add the modifier.
        Returns a numpy array of totals.
        """
        # Fast path: all dice are the same
        if len(self.dice) == 1:
            return self.dice[0].roll(n_simulations) + self.modifier
        # Otherwise, sum each die's rolls
        results = np.zeros(n_simulations, dtype=int)
        for die in self.dice:
            results += die.roll(n_simulations)
        results += self.modifier
        return results

    @staticmethod
    def roll_static(dice: List[Die], modifier: int = 0, n_simulations: int = 1) -> np.ndarray:
        """
        Static method version: roll a list of dice with a modifier, no need to instantiate Roll.
        """
        if len(dice) == 1:
            return dice[0].roll(n_simulations) + modifier
        results = np.zeros(n_simulations, dtype=int)
        for die in dice:
            results += die.roll(n_simulations)
        results += modifier
        return results

    def __repr__(self):
        dice_str = ', '.join(repr(d) for d in self.dice)
        if self.modifier:
            return f"Roll([{dice_str}], modifier={self.modifier})"
        else:
            return f"Roll([{dice_str}])"

    def __str__(self):
        return self.__repr__()
