#!/bin/bash
mn --custom ./route_topo.py --topo routetopo --controller=remote,ip=127.0.0.1,port=6633 --switch=user

		#  H10:10.0.0.3:h10-eth0
		#  |                H11:10.0.0.4                  H14:10.0.0.7
		# 1|__           ___|          ___             ___/            
		# / 3 \2_______3/ 4 \1_______1/ 5 \3_________2/ 6 \
		# \___/         \___/         \___/           \___/         
		#  3|             \2         /4  2\            /1
		#   |              \        /      \          /
		#   |               \      /        \        / 
		#   |                \    /          \      /
		#  _|1               1\__/2           \3__ /2 
		# /   \2____________3/   \            /   \1-----H13:10.0.0.6:h9-eth0
		# \_1_/              \_2_/            \_7_/       


    #switch[1,2,3,4,5,6,7]
    #host[8,9,···,13,14]
		# CONTROLLER:127.0.0.1:6633
		# CPQD SDN switch





