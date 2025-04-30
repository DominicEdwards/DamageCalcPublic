from abc import ABC, abstractmethod
from enum import Enum

import numpy as np

from src.dice import Die, Roll


class AdvantageState(Enum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


class Action(ABC):
    """Base class for all actions (attack, direct damage, save, etc)."""

    def __init__(self, name: str, probability: float = 1.0):
        self.name = name
        if not (0.0 <= probability <= 1.0):
            raise ValueError("probability must be between 0.0 and 1.0")
        self.probability = probability

    @abstractmethod
    def simulate(self, n_sim: int) -> np.ndarray:
        """
        Simulate the action over a number of simulations.

        :param n_sim: Number of simulations to run.
        :return: A numpy array containing the results of the simulations.
        """
        pass


class AttackAction(Action):
    def __init__(
        self,
        name: str,
        ac: int,
        crit_value: int,
        damage_die,
        mod: int,
        proficiency: int,
        d20: Die,
        bonus_attack_mod: int = 0,
        advantage: str = "normal",
        probability: float = 1.0,
    ):
        super().__init__(name, probability=probability)
        if ac < 1:
            raise ValueError("Armor Class (ac) must be at least 1.")
        if crit_value < 1 or crit_value > 20:
            raise ValueError("crit_value must be between 1 and 20.")
        if not isinstance(damage_die, (Die, Roll)):
            raise TypeError("damage_die must be a Die or Roll instance.")
        if not isinstance(d20, Die):
            raise TypeError("d20 must be a Die instance.")
        self.mod = mod
        self.proficiency = proficiency
        self.bonus_attack_mod = bonus_attack_mod
        self.ac = ac
        self.crit_value = crit_value
        self.damage_die = damage_die
        self.d20 = d20
        # Accepts 'normal', 'advantage', 'disadvantage', or bool (True/False)
        if isinstance(advantage, bool):
            self.advantage = AdvantageState.ADVANTAGE if advantage else AdvantageState.NORMAL
        elif isinstance(advantage, str):
            self.advantage = AdvantageState(advantage.lower())
        else:
            self.advantage = AdvantageState.NORMAL

    def simulate(self, n_sim: int) -> np.ndarray:
        # Use advantage/disadvantage logic
        if self.advantage == AdvantageState.NORMAL:
            attack_rolls = self.d20.roll(n_sim)
        else:
            rolls = self.d20.roll(n_sim * 2).reshape(n_sim, 2)
            if self.advantage == AdvantageState.ADVANTAGE:
                attack_rolls = np.maximum(rolls[:, 0], rolls[:, 1])
            else:  # DISADVANTAGE
                attack_rolls = np.minimum(rolls[:, 0], rolls[:, 1])
        total_attack_mod = self.proficiency + self.mod + self.bonus_attack_mod
        totals = attack_rolls + total_attack_mod
        crits = attack_rolls >= self.crit_value
        hits = (totals >= self.ac) | crits
        normal_hit_damage = self.damage_die.roll(n_sim) + self.mod
        crit_rolls = self.damage_die.roll(n_sim * 2).reshape(n_sim, 2)
        crit_damage = np.sum(crit_rolls, axis=1) + self.mod
        damage = np.zeros(n_sim)
        damage[crits] = crit_damage[crits]
        damage[hits & ~crits] = normal_hit_damage[hits & ~crits]
        # Apply probability mask
        if self.probability < 1.0:
            mask = np.random.rand(n_sim) < self.probability
            damage = damage * mask
        return damage

    def __str__(self):
        return (f"AttackAction(name={self.name}, ac={self.ac}, crit_value={self.crit_value}, "
                f"damage_die={self.damage_die}, mod={self.mod}, proficiency={self.proficiency}, "
                f"bonus_attack_mod={self.bonus_attack_mod}, advantage={self.advantage.name}, probability={self.probability})")

    def __repr__(self):
        return self.__str__()


class DirectDamageAction(Action):
    def __init__(self, name: str, damage_die, modifier: int = 0, probability: float = 1.0):
        super().__init__(name, probability=probability)
        if not isinstance(damage_die, (Die, Roll)):
            raise TypeError("damage_die must be a Die or Roll instance.")
        self.damage_die = damage_die
        self.modifier = modifier

    def simulate(self, n_sim: int) -> np.ndarray:
        damage = self.damage_die.roll(n_sim) + self.modifier
        if self.probability < 1.0:
            mask = np.random.rand(n_sim) < self.probability
            damage = damage * mask
        return damage

    def __str__(self):
        return (f"DirectDamageAction(name={self.name}, damage_die={self.damage_die}, "
                f"modifier={self.modifier}, probability={self.probability})")

    def __repr__(self):
        return self.__str__()


class SaveAction(Action):
    def __init__(
        self,
        name: str,
        dc: int,
        save_bonus: int,
        damage_die,
        modifier: int = 0,
        half_on_success: bool = True,
        d20: Die = None,
        probability: float = 1.0,
    ):
        super().__init__(name, probability=probability)
        if dc < 1:
            raise ValueError("DC must be at least 1.")
        if not isinstance(damage_die, (Die, Roll)):
            raise TypeError("damage_die must be a Die or Roll instance.")
        if d20 is not None and not isinstance(d20, Die):
            raise TypeError("d20 must be a Die instance if provided.")
        self.dc = dc
        self.save_bonus = save_bonus
        self.damage_die = damage_die
        self.modifier = modifier
        self.half_on_success = half_on_success
        self.d20 = d20 or Die(20)

    def simulate(self, n_sim: int) -> np.ndarray:
        save_rolls = self.d20.roll(n_sim) + self.save_bonus
        failed = save_rolls < self.dc
        damage_full = self.damage_die.roll(n_sim) + self.modifier
        if self.half_on_success:
            damage = np.where(failed, damage_full, damage_full // 2)
        else:
            damage = np.where(failed, damage_full, 0)
        if self.probability < 1.0:
            mask = np.random.rand(n_sim) < self.probability
            damage = damage * mask
        return damage

    def __str__(self):
        return (f"SaveAction(name={self.name}, dc={self.dc}, save_bonus={self.save_bonus}, "
                f"damage_die={self.damage_die}, modifier={self.modifier}, half_on_success={self.half_on_success}, "
                f"probability={self.probability})")

    def __repr__(self):
        return self.__str__()
