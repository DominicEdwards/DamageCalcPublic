from typing import List

import logging
import numpy as np


class FightComparison:
    """Compare the results of multiple actions or rounds."""

    def __init__(self, fight_results: List[np.ndarray], labels: List[str] = None):
        self.fight_results = fight_results
        self.labels = labels if labels else [f"Action {i+1}" for i in range(len(fight_results))]
        self.n = len(fight_results)
        self.n_sim = len(fight_results[0]) if fight_results else 0

    def summary(self):
        for i, (label, dmg) in enumerate(zip(self.labels, self.fight_results)):
            logging.info(f"{label}: Expected damage = {np.mean(dmg):.3f}")

    def pairwise_probs(self):
        for i in range(self.n):
            for j in range(i + 1, self.n):
                prob_i_beats_j = np.mean(self.fight_results[i] > self.fight_results[j])
                prob_j_beats_i = np.mean(self.fight_results[j] > self.fight_results[i])
                prob_equal = np.mean(self.fight_results[i] == self.fight_results[j])
                logging.info(f"P({self.labels[i]} > {self.labels[j]}): {prob_i_beats_j:.3%}")
                logging.info(f"P({self.labels[j]} > {self.labels[i]}): {prob_j_beats_i:.3%}")
                logging.info(f"P({self.labels[i]} == {self.labels[j]}): {prob_equal:.3%}\n")
