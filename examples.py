import random
from classes import *


def random_walk_update(hunters: tuple[int], prey: tuple[int], foods: dict, maze: dict) -> Movement: 
    return random.choice(maze[prey])

random_walk_prey  = prey(random_walk_update) 

def hunter_random_walk_update(hunters : tuple[int], prey: tuple[int], foods: dict, maze: dict) -> list[Movement]: 
    return [random.choice(maze[hunter]) for hunter in hunters]     

random_walk_hunter = hunters(hunter_random_walk_update)  
