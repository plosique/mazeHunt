import pygame 
import copy
from enum import Enum
from classes import Movement

from examples import *
from competitive_agents import *

#replace these with the versions you want to test 
prey_player = random_walk_prey 
hunter_player  = random_walk_hunter


# some constant setup 
WIDTH  = 720
HEIGHT = 720

SCREENTOMAZERATIO = 0.8

MAZEWIDTH  = SCREENTOMAZERATIO*WIDTH
MAZEHEIGHT = SCREENTOMAZERATIO*HEIGHT

MAZEWIDTHOFFSET  = (WIDTH-MAZEWIDTH)//2
MAZEHEIGHTOFFSET = (HEIGHT-MAZEHEIGHT)//2

NUMROWS = 10
NUMCOLS = 10

ROWSIZE = MAZEHEIGHT/NUMROWS
COLSIZE = MAZEWIDTH/NUMCOLS

NUMhunterS = 4

#some global variable setup 
foods = [[True for _ in range(NUMROWS)] for j in range(NUMCOLS)]

#setup edges 
edges = set()
for i in range(NUMROWS):
    for j in range(NUMCOLS):
            ip = i+1 
            jp = j+1
            if ip == NUMROWS:
                ip = 0 
            if jp == NUMCOLS: 
                jp = 0
            edges.add(tuple(sorted([(i,j),(ip,j)])))
            edges.add(tuple(sorted([(i,j),(i,jp)])))
deleted_edges = set()
# the following two functions will gurantee the invariant edges + deleted edges = total edges
def remove_edge(edge: tuple[int]) -> None:
    edges.remove(edge)
    deleted_edges.add(edge)

def add_edge(edge: tuple[int]) -> None:
    deleted_edges.remove(edge)
    edges.add(edge)

#global hunters and prey
hunters = [(NUMCOLS//2, NUMROWS//2), (NUMCOLS//2, NUMROWS//2-1), (NUMCOLS//2-1,NUMROWS//2),(NUMCOLS//2-1,NUMROWS//2-1)]
prey = (0,0)


def edge2Barrier(n0: tuple[int],n1: tuple[int], x0: float, y0: float,x_size: float, y_size: float) -> tuple[tuple[float]]:    
    """
    Convert an edge to a tuple of tuples representing a line
    """
    i0, j0 = n0
    i1, j1 = n1 
    class Direction(Enum):
        LEFT, UP, RIGHT, DOWN = range(4) 

    # Establish a direction that the edge is heading 
    if i1 == (i0 - 1)%NUMCOLS and j1 == j0:
        dir = Direction.LEFT 
    elif i1 == i0 and j1 == (j0 - 1)%NUMROWS:
        dir = Direction.UP
    elif i1 == (i0+1)%NUMCOLS and j1 == j0:
        dir = Direction.RIGHT
    elif i1 == i0 and j1 == (j0 + 1)%NUMROWS:
        dir = Direction.DOWN 
    else: 
        raise ValueError("Nodes are not adjacent") 

    #Construct line based off that direction and the initial node
    if dir == Direction.LEFT:
        x_source, y_source = x0 + i0*x_size, y0 + j0*y_size 
        x_dest, y_dest     = x_source, y_source+y_size  
    elif dir == Direction.UP: 
        x_source, y_source = x0 + i0*x_size, y0 + j0*y_size 
        x_dest, y_dest     = x_source + x_size, y_source 
    elif dir == Direction.RIGHT:
        x_source, y_source = x0 + (i0+1)*x_size, y0 + j0*y_size
        x_dest, y_dest      = x_source, y_source + y_size 
    elif dir == Direction.DOWN:
        x_source, y_source = x0+i0*x_size, y0 + (j0+1)*y_size 
        x_dest, y_dest     = x_source+x_size, y_source 
    
    return ((x_source, y_source),(x_dest,y_dest))

def swapEdge(x: float,y: float ,x0: float,y0: float,x_size: float,y_size: float) -> None:
    """ 
    Check if point is close to an edge.
    If the edge is in the edge set remove it, otherwise add it back
    """
    ix = int((x-x0)/x_size)
    iy = int((y-y0)/y_size)

    if 0<=ix and ix<NUMCOLS and 0<=iy and iy<NUMROWS: # check point is in maze
        left = x0+x_size*ix
        top  = y0+y_size*iy

        #grab all four lines around the point clicked
        line_top    = ((left,top),(left+x_size,top))
        line_right  = ((left+x_size,top),(left+x_size,top+y_size))
        line_bottom = ((left,top+y_size),(left+x_size,top+y_size))
        line_left   = ((left,top),(left,top+y_size)) 

        dist_lines_node = [(y-top,line_top,(ix,iy-1)),(left+x_size-x,line_right,(ix+1,iy)),(top+y_size-y,line_bottom,(ix,iy+1)),(x-left,line_left,(ix-1,iy))]

        dist = dist_lines_node[0][0] 
        line = dist_lines_node[0][1]
        node = dist_lines_node[0][2]

        #find the closest line 
        for tup in dist_lines_node[1:]:
            d,l,n = tup
            if d < dist: 
                dist= d
                line = l 
                node  = n
        node = (node[0]%NUMCOLS, node[1]%NUMROWS)  

        # if the point is close enough to the edge then swap the edge. 
        if dist*dist < x_size*y_size/25:
            edge = tuple(sorted([(ix,iy),node]))
            #swap edge 
            if edge in deleted_edges:
                add_edge(edge)
            else: 
                remove_edge(edge)

def drawhunters(hunters: list[tuple[int]], _screen) -> None: 
    for hunter in hunters: 
        x = hunter[0]*COLSIZE + COLSIZE/2 + MAZEWIDTHOFFSET
        y = hunter[1]*ROWSIZE + ROWSIZE/2 + MAZEHEIGHTOFFSET 
        pygame.draw.circle(_screen, "black", (x,y),min(COLSIZE,ROWSIZE)/2) 

def drawprey(prey: tuple[int], _screen) -> None: 
    x = prey[0]*COLSIZE + COLSIZE/2 + MAZEWIDTHOFFSET 
    y = prey[1]*ROWSIZE + ROWSIZE/2 + MAZEHEIGHTOFFSET
    pygame.draw.circle(_screen, "yellow",(x,y), min(COLSIZE,ROWSIZE)/2)

def drawFood(_foods: list[list[bool]], _screen) -> None:
    width = min(ROWSIZE,COLSIZE)/2
    for i in range(NUMROWS):
        for j in range(NUMCOLS):
            if _foods[i][j]: 
                x = MAZEWIDTHOFFSET + COLSIZE/4 + i*COLSIZE
                y = MAZEHEIGHTOFFSET + ROWSIZE/4 + j*ROWSIZE
                pygame.draw.rect(screen,"blue",pygame.Rect(x, y, width, width))  

def battle(prey: tuple[int], hunters: list[tuple[int]]) -> tuple[list[tuple[int]]]: 
    def update_square(square: tuple[int], move: Movement) -> tuple[int]: 
        i,j = square
        if move == Movement.NORTH:
            res = (i,j-1) 
        elif move == Movement.SOUTH:
            res = (i,j+1) 
        elif move == Movement.EAST:
            res = (i-1,j) 
        elif move == Movement.WEST:
            res = (i+1,j) 
        elif move == Movement.WAIT: 
            res = (i,j) 
        return (res[0]%NUMCOLS, res[1]%NUMROWS) 
            
    #create the maze 
    # maps edges to corresponding movements 
    maze = {} 
    for i in range(NUMROWS):
        for j in range(NUMCOLS):
            maze[(i,j)] = [Movement.WAIT]

    for edge in edges: 
        x0,y0 = edge[0]
        x1,y1 = edge[1] 
        x = (x1-x0)  
        y = (y1-y0)
        #do toroidal stuff 
        if x == -NUMCOLS+1: 
            x = 1 
        if x == NUMCOLS-1: 
            x = -1
        if y == -NUMROWS+1: 
            y = 1 
        if  y == NUMROWS-1: 
            y = -1  

        if y == -1: 
            move = (Movement.NORTH, Movement.SOUTH)  
        elif y == 1: 
            move = (Movement.SOUTH,Movement.NORTH) 
        elif x == -1: 
            move = (Movement.EAST, Movement.WEST) 
        elif x == 1: 
            move = (Movement.WEST, Movement.EAST) 
        else: 
            raise ValueError(f"{i} : {j}")
        

        maze[edge[0]].append(move[0])  
        maze[edge[1]].append(move[1]) 

    num_moves = 1000 # prevents battle from infinitely looping 
    prey_player_squares = [prey] #tracks prey nodes 
    hunter_player_squares  = [hunters.copy()] #tracks hunter nodes

    prey_caught = False 
    _foods = copy.deepcopy(foods) 
    ct = 0 
    #run battler tracking moves 
    while ct < num_moves and not prey_caught: 
        ct+=1
        _foods[prey[0]][prey[1]] = False #prey eats food  
        #get moves 
        p_move = prey_player.update(hunters, prey, _foods, maze)   
        g_moves = hunter_player.update(hunters, prey, _foods, maze)
        #updates positions 
        prey = update_square(prey, p_move) 
        for i in range(NUMhunterS): 
            hunters[i] = update_square(hunters[i],g_moves[i]) 
        #add to square lists
        prey_player_squares.append(prey)
        hunter_player_squares.append(hunters.copy()) 
        #check if prey caught 
        for hunter in hunters: 
            prey_caught = prey_caught or hunter == prey 
    return prey_player_squares, hunter_player_squares
def drawMaze(deleted_edges: set, num_rows: int, num_cols: int, x_offset: float, y_offset: float, col_size: int, row_size: int, _screen) -> None: 
    
    #draw outer rectangle
    outline_width = 20
    outline = pygame.Rect(x_offset-outline_width,y_offset-outline_width,MAZEWIDTH+2*outline_width,MAZEHEIGHT+2*outline_width)
    pygame.draw.rect(_screen,'red',outline,outline_width,1)

    #draw grid
    for i in range(num_cols):
        x = x_offset + i*col_size
        pygame.draw.line(_screen,'black',(x,y_offset),(x,y_offset+MAZEHEIGHT))  

    for i in range(num_rows):
        y = y_offset + i*row_size
        pygame.draw.line(_screen,'black',(x_offset,y),(x_offset+MAZEWIDTH,y))  

    #draw barriers in place of the deleted edges
    for edge in deleted_edges:
        line0,line1 = edge2Barrier(edge[0],edge[1],x_offset,y_offset,col_size,row_size)
        pygame.draw.line(_screen,'black',line0,line1,3)  
    
if __name__ == '__main__':
          
    #initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    #initialize font 
    pygame.font.init() 
    CMS_FONT = pygame.font.SysFont('Comic Sans MS', 25)
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))

    #initalize edges 
    deleted_edges = set()

    #initialize score 
    score = 0

    #useful aliases
    row_size = MAZEWIDTH/NUMCOLS
    col_size = MAZEHEIGHT/NUMROWS

    class Actions(Enum):
        NOTHING, QUIT, SWAP_BARRIER, BATTLE = 0, 1, 2, 3
    
    action = Actions.NOTHING
    while action != Actions.QUIT:  
        screen.fill('white') # wipe away last frame
        action = Actions.NOTHING 
        mousex, mousey = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                action = Actions.QUIT
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = Actions.SWAP_BARRIER
            if event.type == pygame.TEXTINPUT:
                if event.text == 'b': 
                    action = Actions.BATTLE  
    
        if action is Actions.SWAP_BARRIER:
            swapEdge(mousex,mousey,MAZEWIDTHOFFSET, MAZEHEIGHTOFFSET, col_size,row_size)
        elif action is Actions.BATTLE: 
            # simulate battle 
            prey_squares, hunter_squares = battle(prey, hunters.copy())
            #draw simulation 
            score = 0 
            _foods = copy.deepcopy(foods)
            _hunters = hunters.copy()
            _prey = prey  
            _score  = 0  
            for i in range(len(prey_squares)): 
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        action = Actions.QUIT
                if action == Actions.QUIT:
                    break
                _prey = prey_squares[i] 
                _hunters = hunter_squares[i] 
                _score += _foods[_prey[0]][_prey[1]]*10
                _foods[_prey[0]][_prey[1]] = False
                screen.fill('white') # wipe away last frame
                drawMaze(deleted_edges, NUMCOLS, NUMROWS, MAZEWIDTHOFFSET, MAZEHEIGHTOFFSET, col_size, row_size, screen)
                drawFood(_foods, screen)
                drawprey(_prey, screen) 
                drawhunters(_hunters, screen) 
                text_surface = CMS_FONT.render(f'score: {_score}', True, 'black')
                screen.blit(text_surface,(0,0)) 
                clock.tick(2) 
                pygame.display.flip() 
            print(f"final score: {_score}") 
            pygame.event.clear()


        
        drawMaze(deleted_edges, NUMCOLS, NUMROWS, MAZEWIDTHOFFSET, MAZEHEIGHTOFFSET, col_size, row_size, screen)
        drawFood(foods, screen)
        drawprey(prey, screen) 
        drawhunters(hunters, screen) 
        text_surface = CMS_FONT.render(f'score: {score}', True, 'black')
        screen.blit(text_surface,(0,0)) 
        clock.tick(60) 
        pygame.display.flip()
        
        
