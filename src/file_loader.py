import os
import json
import re
import logging
try:
    import yaml
except ImportError:
    yaml = None

from src.actions import AttackAction, DirectDamageAction, SaveAction
from src.dice import Die

def load_actions_from_file(path, d20=Die(20)):
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'r') as f:
        if ext in ['.yaml', '.yml']:
            if yaml is None:
                raise ImportError('PyYAML is required for YAML input files. Install with `pip install pyyaml`.')
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    actions = []

    def parse_die(die_value):
        if isinstance(die_value, int):
            return Die(die_value)
        if isinstance(die_value, str):
            return Die.parse(die_value)
        raise TypeError(f"Unsupported die value type: {type(die_value)}")

    def attack_action_factory(entry):
        probability = entry.get('probability', 1.0)
        return AttackAction(
            entry['name'],
            entry['ac'],
            entry['crit_min'],
            parse_die(entry['die']),
            entry['mod'],
            entry['proficiency'],
            d20,
            entry.get('bonus_attack_mod', 0),
            entry.get('advantage', 'normal'),
            probability=probability
        )

    def direct_damage_action_factory(entry):
        return DirectDamageAction(
            entry['name'],
            parse_die(entry['die']),
            entry['num_dice']
        )

    def save_action_factory(entry):
        return SaveAction(
            entry['name'],
            dc=entry['dc'],
            save_bonus=entry['save_bonus'],
            damage_die=parse_die(entry['die']),
            modifier=entry.get('modifier', 0),
            half_on_success=entry.get('half_on_success', False),
            d20=d20
        )

    action_factories = {
        'AttackAction': attack_action_factory,
        'DirectDamageAction': direct_damage_action_factory,
        'SaveAction': save_action_factory
    }

    for entry in data.get('actions', []):
        kind = entry.get('type')
        factory = action_factories.get(kind)
<<<<<<< HEAD
        repeat = entry.get('repeat', 1)
        if factory:
            try:
                for _ in range(repeat):
                    action = factory(entry)
                    actions.append(action)
                logging.info(f"Loaded action: {entry.get('name', '<unnamed>')} (type: {kind}, repeat: {repeat})")
            except Exception as e:
                logging.error(f"Failed to load action {entry.get('name', '<unnamed>')}: {e}")
        else:
            logging.warning(f"Unknown action type: {kind} in entry: {entry}")
    if not actions:
        logging.warning("No valid actions loaded from file.")
=======
        if factory:
            actions.append(factory(entry))
>>>>>>> origin/development
    return actions
