from game import *
import random
import pandas as pd



board = Board()

print(f'Len of list_routes: {len(board.spot_manager.list_routes())}')

for number in range(199):
    spot = Spot(number + 1)
    board.__add_spot(spot)

spot = board.spot_list[13]
print(spot.number)


print(f"Len of list_routes: {len(board.spot_manager.list_routes())}")

