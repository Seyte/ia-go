# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from random import choice
from playerInterface import *
import signal
import copy 

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''
    MAX_VALUE = 10000

    # simplest heuristic possible for this game.
    def heuristic(self,board): 
        return self.heuristique_complexe(board)
        #Black make the first move.
        scores = board.compute_score() # BLACK / WHITE
        if (self._mycolor == Goban.Board._BLACK):
            return (scores[0]-scores[1])
        elif (self._mycolor == Goban.Board._WHITE):
            return (scores[1]-scores[0])
        else: #shouldn't go in there. fallback.
            return 0
    
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._last_best_move = None
        self._play_time = 1 # to cover additional time we can't mesure.

    def getRoundTime(self):
        return min(10,(1800-self._play_time)/100)
    
    def getWinnerColor(self,board):
        result = board.result()
        if result == "1-0":
            if (self._mycolor == Goban.Board._WHITE):
                return self.MAX_VALUE
            return -self.MAX_VALUE
        elif result == "0-1":
            if (self._mycolor == Goban.Board._BLACK):
                return self.MAX_VALUE
            return -self.MAX_VALUE
        return 0
    
    def getBoardCopy(self):
        board = Goban.Board()
        for move in self._all_moves:
            board.push(move)
        return board
    
    def getPlayerName(self):
        return "MinimaxPlayer"

    def heuristique_simple(self,board):
        assert(self._mycolor != None)
        result = board.diff_stones_board() + 2*board.diff_stones_captured()
        if (self._mycolor == Goban.Board._BLACK):
            return result
        elif (self._mycolor == Goban.Board._WHITE):
            return -result
        return 0
    
    def heuristique_complexe(self,board):
        assert(self._mycolor != None)
        array = board.get_board()
        holes_in_black = 0
        holes_in_white = 0
        for i in range(9):
            for j in range(9):
                if (array[i+9*j] == Goban.Board._EMPTY):
                    if (((i == 0) or (array[(i-1)+9*j] == Goban.Board._BLACK))
                        and ((i == 8) or (array[(i+1)+9*j] == Goban.Board._BLACK))
                        and ((j == 0) or (array[i+9*(j-1)] == Goban.Board._BLACK))
                        and ((j == 8) or (array[i+9*(j+1)] == Goban.Board._BLACK))):
                        holes_in_black += 1
                    elif (((i == 0) or (array[(i-1)+9*j] == Goban.Board._WHITE))
                        and ((i == 8) or (array[(i+1)+9*j] == Goban.Board._WHITE))
                        and ((j == 0) or (array[i+9*(j-1)] == Goban.Board._WHITE))
                        and ((j == 8) or (array[i+9*(j+1)] == Goban.Board._WHITE))):
                        holes_in_white += 1
        result = holes_in_black - holes_in_white
        if (self._mycolor == Goban.Board._BLACK):
            return 2*result + self.heuristique_simple(board)
        elif (self._mycolor == Goban.Board._WHITE):
            return -2*result + self.heuristique_simple(board)
        return 0
        
    def handler(self,signum, frame):
        raise TimeoutError("Timeout")
    
    def simulateFriendlyMove(self,board,current_depth,max_depth,alpha,beta):
        if (current_depth>=max_depth or board._gameOver):
            if (board._gameOver):
                return self.getWinnerColor(board)
            return self.heuristic(board),None
        best_move = None
        for l in board.generate_legal_moves() :
            board.push(l)
            e = self.simulateEnnemyMove(board,current_depth+1,max_depth,alpha,beta)
            new = max(alpha,e[0])
            if (new>alpha):
                alpha = new
                best_move = l
            board.pop()
            if (alpha>=beta):
                return beta,best_move
        return alpha,best_move

    def simulateEnnemyMove(self,board,current_depth,max_depth,alpha,beta):
        if (current_depth>=max_depth or board._gameOver):
            if (board._gameOver):
                return self.getWinnerColor(board)
            return self.heuristic(board),None

        best_move = None
        for l in board.generate_legal_moves() :
            board.push(l)
            a = self.simulateFriendlyMove(board,current_depth+1,max_depth,alpha,beta)
            new = min(beta,a[0])
            if (beta>new):
                beta = new
                best_move = l
            board.pop()
            if (alpha >= beta):
                return alpha,best_move
        return beta,best_move

    def start_deep(self,board,current_depth,max_depth):
        if (not (board.is_game_over())):
            a = self.simulateFriendlyMove(board,current_depth,max_depth,-5000,5000)
            return a[1]
    
    def getPlayerMove(self):
        currentTime = time.time()
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        
        moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        self._last_best_move = choice(moves) 
        max_depth = 1
        original_sigalarm_handler = None
        try :
            original_sigalarm_handler = signal.signal(signal.SIGALRM, self.handler)
            while(True):
                signal.alarm(self.getRoundTime())
                self._last_best_move = self.start_deep(copy.deepcopy(self._board),0,max_depth)
                max_depth+=1
        except TimeoutError:
            pass # if we do not use iterative deepening.
        finally:
            print("I got to explore until " + str(max_depth-1))
            self._board.push(self._last_best_move)
            # New here: allows to consider internal representations of moves
            print("I am playing ", self._board.move_to_str(self._last_best_move))
            print("My current board :")
            self._board.prettyPrint()
            self._play_time += time.time() - currentTime
            print("Player time = " + str(self._play_time))
            # move is an internal representation. To communicate with the interface I need to change if to a string
            return Goban.Board.flat_to_name(self._last_best_move) 


    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("Minimax : I won!!!")
        else:
            print("Minimax : I lost :(!!")



