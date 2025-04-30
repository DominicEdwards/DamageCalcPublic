# D&D Damage Calculator

This project simulates D&D 5e combat rounds, attacks, spells, and other effects to compare damage output and probabilities.

## Structure
- `src/`: Core logic modules (actions, dice, rounds, etc.)
- `tests/`: Unit tests (pytest)
- `simulate_fight.py`: Example script to run simulations and comparisons

## Install
```
pip install -r requirements.txt
```

## Run Example
```
python simulate_fight.py
```

## Run Tests
```
python -m pytest tests/
```

## Modules
- `actions.py`: Action classes (Attack, Direct Damage, Save, etc.)
- `dice.py`: Die and dice-rolling utilities
- `rounds.py`: Round logic (multiple actions per round)
- `comparison.py`: Damage/statistics comparison utilities
- `attack_rolls.py`, `damage_options.py`: Additional mechanics

## Requirements
- Python 3.8+
- numpy
- pytest (for tests)

## Usage

You can run the main simulation with configurable options:

```sh
# Single mode (simulate actions from one file)
python simulate_fight.py --actions_file example_actions.yaml --n_sim 100000

# Comparison mode (compare two builds/strategies)
python simulate_fight.py --build1_file build1.yaml --build2_file build2.yaml --n_sim 100000
```

All arguments are optional and have sensible defaults. Results and statistics will be logged to the console and saved to `simulation_results.csv`.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository and create a new branch.
2. Make your changes, ensuring code is formatted with `black` and passes `ruff` linting.
3. Add or update tests in the `tests/` directory.
4. Open a pull request with a clear description of your changes.

### Development Setup

- Install dependencies: `pip install -r requirements.txt`
- Run tests: `python -m pytest tests/`
- Format code: `black .`
- Lint code: `ruff .`

## Dice Usage

This project provides flexible dice-rolling utilities via the `Die` and `Roll` classes in `src/dice.py`. You can use standard dice notation and advanced options:

### Supported Notation
- `d6` — roll one six-sided die
- `2d8+3` — roll two eight-sided dice and add 3
- `d10min2` — roll a d10, but treat any result less than 2 as 2 (Great Weapon Fighting style)
- `d6r1` — roll a d6, rerolling any 1s until a non-1 is rolled
- `d8r1x2` — roll a d8, rerolling 1s, but at most 2 rerolls per die

### Programmatic Usage
You can use the `Die` and `Roll` classes directly in your code:

```python
from src.dice import Die, Roll

# Roll a d20
result = Die(20).roll()

# Roll 3d6 and sum the results
roll = Roll([Die(6) for _ in range(3)])
result = roll.roll()

# Parse dice notation
parsed = Die.parse('2d6+3')
result = parsed.roll()
```

### In Action Files
When specifying actions in YAML/JSON files, you can use these notations for damage or attack rolls. The parser will automatically interpret them.

See `src/dice.py` for more advanced options and details.
