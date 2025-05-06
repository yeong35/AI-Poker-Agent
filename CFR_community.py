from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
import numpy as np

# CFR logic learning
class CFRTrainer:
    def __init__(self):
        self.regret_sum = dict()    # accumulated regret
        self.strategy_sum = dict()  # stratergies probabilites

    def get_strategy(self, info_set, num_actions):
        # If a strategy for this info_set was pre-trained and loaded from JSON, use it.
        # not for train
        # if info_set in self.strategy_sum and len(self.strategy_sum[info_set]) == num_actions:
        #     strat = self.strategy_sum[info_set]
        #     total = sum(strat)
        #     if total > 0:
        #         return [s / total for s in strat]
        
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

class CFR_com(BasePokerPlayer):
    def __init__(self, trainer=None):
        self.trainer = trainer if trainer is not None else CFRTrainer()
        self.history = []
        self.uuid = None  
        
    def declare_action(self, valid_actions, hole_card, round_state):
        info_set = self._get_info_set(hole_card, round_state)
        strategy = self.trainer.get_strategy(info_set, len(valid_actions))
        action_idx = np.random.choice(len(valid_actions), p=strategy)

        # print(f"\n[INFO] InfoSet: {info_set}")
        # print(f"[INFO] Strategy: {strategy}")
        # print(f"[INFO] Action: {valid_actions[action_idx]['action']}")

        self.history.append((info_set, action_idx, strategy))

        return valid_actions[action_idx]["action"]

    def _get_info_set(self, hole_card, round_state):
        # hands
        hole_ranks = sorted([card[1] for card in hole_card])  # e.g.) ['4', 'K'] → '4K'
        hole_str = ''.join(hole_ranks)

        # community cards
        community = round_state.get('community_card', [])
        board_ranks = sorted([card[1] for card in community]) if community else []
        board_str = ''.join(board_ranks) if board_ranks else 'none'

        # return information set (without street)
        return f"hand{hole_str}_board{board_str}"



    def receive_round_result_message(self, winners, hand_info, round_state):
        # calcuate utilities
        stacks = {p['uuid']: p['stack'] for p in round_state['seats']}
        my_stack = stacks[self.uuid]
        opp_stack = [s for uuid, s in stacks.items() if uuid != self.uuid][0]

        
        # check self.player_id to update each regret
        player_id = 0 if self.uuid == round_state['seats'][0]['uuid'] else 1

        # set utillity
        util = [0.0, 0.0]
        if my_stack > opp_stack:
            util[player_id] = 1.0
            util[1-player_id] = -1.0
        elif my_stack < opp_stack:
            util[player_id] = -1.0
            util[1-player_id] = 1.0
    
        self.trainer.update_regret(self.history, util, player_id)

        # history reset
        self.history = []
    
    def receive_game_start_message(self, game_info):
        pass
    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass
def setup_ai():
  return CFR_com()
