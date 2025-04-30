import numpy as np
import pytest
from src.dice import Die
from src.actions import AttackAction, DirectDamageAction, SaveAction

class DummyDie(Die):
    def __init__(self, value):
        self.value = value
        self.sides = value
        self.min_value = None
        self.reroll = None
        self.max_rerolls = None
    def roll(self, n=1):
        return np.full(n, self.value)

def test_attack_action_hit_and_crit():
    d20 = DummyDie(20)
    damage_die = DummyDie(8)
    action = AttackAction(
        name="Test Attack",
        ac=10,
        crit_value=20,
        damage_die=damage_die,
        mod=3,
        proficiency=2,
        d20=d20,
        bonus_attack_mod=0,
    )
    result = action.simulate(10)
    assert np.all(result >= 0)

def test_direct_damage_action():
    damage_die = DummyDie(6)
    action = DirectDamageAction("Test Direct", damage_die, modifier=2)
    result = action.simulate(5)
    assert np.all(result == 8)

def test_save_action_half_on_success():
    d20 = DummyDie(10)
    damage_die = DummyDie(12)
    action = SaveAction(
        name="Test Save",
        dc=15,
        save_bonus=10,
        damage_die=damage_die,
        modifier=0,
        half_on_success=True,
        d20=d20,
    )
    result = action.simulate(4)
    # All saves succeed (10+10=20 > 15), so all damage should be halved
    assert np.all(result == 6)

def test_save_action_no_damage_on_success():
    d20 = DummyDie(10)
    damage_die = DummyDie(12)
    action = SaveAction(
        name="Test Save",
        dc=15,
        save_bonus=10,
        damage_die=damage_die,
        modifier=0,
        half_on_success=False,
        d20=d20,
    )
    result = action.simulate(4)
    # All saves succeed, so all damage should be 0
    assert np.all(result == 0)
