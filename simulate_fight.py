import numpy as np

from src.comparison import FightComparison
from src.dice import Die
from src.file_loader import load_actions_from_file
import logging
import argparse
import os
import json
try:
    import yaml
except ImportError:
    yaml = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser(description="Simulate D&D 5e combat rounds and damage.")
    parser.add_argument('--n_sim', type=int, default=100_000, help='Number of simulations')
    parser.add_argument('--actions_file', type=str, default=None, help='Path to JSON or YAML file specifying actions (single damage mode)')
    parser.add_argument('--build1_file', type=str, default=None, help='First build file for comparison mode')
    parser.add_argument('--build2_file', type=str, default=None, help='Second build file for comparison mode')
    args = parser.parse_args()

    n_sim = args.n_sim
    d20 = Die(20)

    # Determine mode: single or comparison
    if args.actions_file and not (args.build1_file or args.build2_file):
        # Single mode: sum all actions as a single build
        actions = load_actions_from_file(args.actions_file, d20=d20)
        if not actions:
            logging.info("No actions found in input file.")
        else:
            damages = [action.simulate(n_sim) for action in actions]
            total_damage = np.sum(damages, axis=0)
            avg_damage = np.mean(total_damage)
            logging.info(f"Total average damage per round: {avg_damage:.3f}")
            # Per-action expected damage
            for i, (action, dmg) in enumerate(zip(actions, damages)):
                logging.info(f"  {action.name}: Expected damage = {np.mean(dmg):.3f}")
            # Calculate quantiles for damage distribution
            quantiles = [5, 25, 50, 75, 95]
            quantile_values = np.percentile(total_damage, quantiles)
            logging.info("Damage quantiles (per round):")
            for q, v in zip(quantiles, quantile_values):
                logging.info(f"  {q}th percentile: {v:.2f}")
            # Save results with quantiles and per-action averages
            import pandas as pd
            results = {
                'Build': [os.path.basename(args.actions_file)],
                'Average Damage': [avg_damage],
                '5th Percentile': [quantile_values[0]],
                '25th Percentile': [quantile_values[1]],
                'Median': [quantile_values[2]],
                '75th Percentile': [quantile_values[3]],
                '95th Percentile': [quantile_values[4]],
            }
            # Add per-action expected damage columns
            for i, (action, dmg) in enumerate(zip(actions, damages)):
                results[f'Action {i+1} - {action.name}'] = [np.mean(dmg)]
            df = pd.DataFrame(results)
            df.to_csv('simulation_results.csv', index=False)
            logging.info("Results saved to simulation_results.csv")
    elif args.build1_file and args.build2_file:
        # Comparison mode
        actions1 = load_actions_from_file(args.build1_file, d20=d20)
        actions2 = load_actions_from_file(args.build2_file, d20=d20)
        # Each file is treated as a 'build' or 'strategy', sum their actions per round
        damages1 = np.sum([a.simulate(n_sim) for a in actions1], axis=0)
        damages2 = np.sum([a.simulate(n_sim) for a in actions2], axis=0)
        comparison = FightComparison([damages1, damages2], labels=[os.path.basename(args.build1_file), os.path.basename(args.build2_file)])
        comparison.summary()
        comparison.pairwise_probs()
        # Save results
        import pandas as pd
        results = {
            'Build': [os.path.basename(args.build1_file), os.path.basename(args.build2_file)],
            'Average Damage': [np.mean(damages1), np.mean(damages2)]
        }
        df = pd.DataFrame(results)
        df.to_csv('simulation_results.csv', index=False)
        logging.info("Comparison results saved to simulation_results.csv")
    else:
        logging.info("No valid input file(s) provided. Exiting without running simulations.")
