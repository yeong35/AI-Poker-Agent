import sys
sys.path.insert(0, './pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import time
from argparse import ArgumentParser
import json
""" =========== *Remember to import your agent!!! =========== """
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from fold_player import FoldPlayer
from CFR_hands import CFR_hands
from CFR_community import CFR_com, CFRTrainer
from CFR_simple import CFRSimple
from submission_simple.custom_player import CustomPlayer
#from submission.custom_player import CustomPlayer

# from smartwarrior import SmartWarrior
""" ========================================================= """

""" Example---To run testperf.py with random warrior AI against itself. 

$ python testperf.py -n1 "Random Warrior 1" -a1 RandomPlayer -n2 "Random Warrior 2" -a2 RandomPlayer
"""

def load_strategy(filepath="cfr_strategy.json"):
    with open(filepath, "r") as f:
        strategy_sum = json.load(f)

    trainer = CFRTrainer()
    trainer.strategy_sum = strategy_sum
    return trainer

def testperf(agent_name1, agent1, agent_name2, agent2):		

	# Init to play 500 games of 1000 rounds
	num_game = 500
	max_round = 1000
	initial_stack = 10000
	smallblind_amount = 20

	# Init pot of players
	agent1_pot = 0
	agent2_pot = 0

	# Setting configuration
	config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)

	trainer = load_strategy("10000000_CFR_com.json")

	# Register players
	config.register_player(name=agent_name1, algorithm=CustomPlayer())
	config.register_player(name=agent_name2, algorithm=RaisedPlayer())
	# config.register_player(name=agent_name1, algorithm=agent1())
	# config.register_player(name=agent_name2, algorithm=agent2())
	

	# Start playing num_game games
	for game in range(1, num_game+1):
		print("Game number: ", game)
		game_result = start_poker(config, verbose=0)
		agent1_pot = agent1_pot + game_result['players'][0]['stack']
		agent2_pot = agent2_pot + game_result['players'][1]['stack']
		# print(game_result)

	# save trainer
	# avg_strategy = {}
	# for info_set in trainer.strategy_sum:
	# 	avg_strategy[info_set] = trainer.get_average_strategy(info_set)

	# with open("avg_strategy.json", "w") as f:
	# 	json.dump(avg_strategy, f)

	# check stratergies
	for info_set in list(trainer.strategy_sum.keys())[:10]:
		avg = trainer.get_average_strategy(info_set)
		print(f"{info_set}: {avg}")

	# print result
	print("\n After playing {} games of {} rounds, the results are: ".format(num_game, max_round))
	# print("\n Agent 1's final pot: ", agent1_pot)
	print("\n " + agent_name1 + "'s final pot: ", agent1_pot)
	print("\n " + agent_name2 + "'s final pot: ", agent2_pot)

	# print("\n ", game_result)
	# print("\n Random player's final stack: ", game_result['players'][0]['stack'])
	# print("\n " + agent_name + "'s final stack: ", game_result['players'][1]['stack'])

	if (agent1_pot<agent2_pot):
		print("\n Congratulations! " + agent_name2 + " has won.")
	elif(agent1_pot>agent2_pot):
		print("\n Congratulations! " + agent_name1 + " has won.")
		# print("\n Random Player has won!")
	else:
		print("\n It's a draw!") 


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-n1', '--agent_name1', help="Name of agent 1", default="Your agent", type=str)
    parser.add_argument('-a1', '--agent1', help="Agent 1", default=RandomPlayer())    
    parser.add_argument('-n2', '--agent_name2', help="Name of agent 2", default="Your agent", type=str)
    parser.add_argument('-a2', '--agent2', help="Agent 2", default=RandomPlayer())    
    args = parser.parse_args()
    return args.agent_name1, args.agent1, args.agent_name2, args.agent2

if __name__ == '__main__':
	name1, agent1, name2, agent2 = parse_arguments()

	start = time.time()
	testperf(name1, agent1, name2, agent2)
	end = time.time()

	print("\n Time taken to play: %.4f seconds" %(end-start))