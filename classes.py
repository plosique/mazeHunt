from enum import Enum
class Movement(Enum):
    WAIT, SOUTH, NORTH, EAST, WEST = 0,1,2,3,4

class prey: 
    def __init__(self, _update) -> None:
        self._update = _update
    
    def update(self, hunters : list[tuple[int]], prey: tuple[int], foods : dict, maze: dict) -> Movement: 
        return self._update(hunters, prey, foods, maze) 

class hunters: 
    def __init__(self, _update) -> None:
        self._update = _update

    def update(self, hunters : list[tuple[int]], prey: tuple[int], foods : dict, maze: dict) -> tuple[Movement]: 
        return self._update(hunters, prey, foods, maze)