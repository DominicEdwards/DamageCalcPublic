from typing import List

import numpy as np

from src.actions import Action


class Round:
    """A round is a collection of actions performed by a single character."""

    def __init__(self, actions: List[Action]):
        self.actions = actions

    def simulate(self, n_sim: int) -> np.ndarray:
        damages = [action.simulate(n_sim) for action in self.actions]
        total_damage = np.sum(damages, axis=0)
        return total_damage
