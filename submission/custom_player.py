from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
import numpy as np
import json

# Load pre-trained average strategies from JSON file into a new CFRTrainer.
def load_strategy(filepath="cfr_strategy.json"):
    with open(filepath, "r") as f:
        strategy_sum = json.load(f)

    trainer = CFRTrainer()
    trainer.strategy_sum = strategy_sum
    return trainer

class CFRTrainer:
    def __init__(self):
        self.regret_sum = dict()    # accumulated regret
        self.strategy_sum = dict()  # stratergies probabilites

    def get_strategy(self, info_set, num_actions):
        # If a strategy for this info_set was pre-trained and loaded from JSON, use it.
        if info_set in self.strategy_sum and len(self.strategy_sum[info_set]) == num_actions:
            strat = self.strategy_sum[info_set]
            total = sum(strat)
            if total > 0:
                return [s / total for s in strat]
        
        # set up the regrets
        regrets = self.regret_sum.get(info_set, [0.0] * num_actions)

        if len(regrets) != num_actions:
            regrets = [0.0] * num_actions
            self.regret_sum[info_set] = regrets

        positive_regrets = [max(0, r) for r in regrets]
        normalizing_sum = sum(positive_regrets)

        # Update cumulative strategy sums for averaging over time.
        if normalizing_sum > 0:
            strategy = [r / normalizing_sum for r in positive_regrets]
        else:
            strategy = [1.0 / num_actions] * num_actions
        if info_set not in self.strategy_sum or len(self.strategy_sum[info_set]) != num_actions:
            self.strategy_sum[info_set] = [0.0] * num_actions

        for i in range(num_actions):
            self.strategy_sum[info_set][i] += strategy[i]

        return strategy

    # update regret after every match
    def update_regret(self, history, utility, player):
        # # Assume a 2-player game. Get opponent index.
        opponent = 1 - player

        # Update regrets for all actions based on difference between taken action and strategy.
        for info_set, action_idx, strategy in history:
            if info_set not in self.regret_sum or len(self.regret_sum[info_set]) != len(strategy):
                self.regret_sum[info_set] = [0.0] * len(strategy)
            regrets = self.regret_sum[info_set]

            # regret = (actual reward - expected reward)
            for i in range(len(strategy)):
                regret = (utility[player] - utility[opponent]) * ((1 if i == action_idx else 0) - strategy[i])
                regrets[i] += regret

    # return the average strategy (nomalized)
    def get_average_strategy(self, info_set):
        strat = self.strategy_sum.get(info_set, [])
        total = sum(strat)
        return [s / total for s in strat] if total > 0 else [1.0 / len(strat)] * len(strat)

class CustomPlayer(BasePokerPlayer):
    def __init__(self, trainer=None):
        self.trainer = load_strategy("100000_CFR_simple.json")
        self.history = []
        self.uuid = None  

    def declare_action(self, valid_actions, hole_card, round_state):
        info_set = self._get_info_set(hole_card, round_state)
        strategy = self.trainer.get_strategy(info_set, len(valid_actions))
        action_idx = np.random.choice(len(valid_actions), p=strategy)

        self.history.append((info_set, action_idx, strategy))
        return valid_actions[action_idx]["action"]

    # ex, flop [HQ, DQ] -> pair / turn [H4, D9] -> 49
    # only consider street and hands
    def _get_info_set(self, hole_card, round_state):
        # get rank
        ranks = sorted([card[1] for card in hole_card])
        
        if ranks[0] == ranks[1]:
            return "pair"
        
        return f"{ranks[0]}{ranks[1]}"


    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
  return CustomPlayer()
