# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from random import choice
from playerInterface import *

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "'Not random anymore' Player"

    def heuristique_simple(self):
        assert(self._mycolor != None)
        result = self._board.diff_stones_board() + 2*self._board.diff_stones_captured()
        if (self._mycolor == Goban.Board._BLACK):
            return result
        elif (self._mycolor == Goban.Board._WHITE):
            return -result
        return 0
    
    def heuristique_complexe(self):
        assert(self._mycolor != None)
        array = self._board.get_board()
        holes_in_black = 0
        holes_in_white = 0
        print(array)
        array[1] = Goban.Board._BLACK
        array[9] = Goban.Board._BLACK
        print(array)
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
            return 3*result + heuristique_simple()
        elif (self._mycolor == Goban.Board._WHITE):
            return -3*result + heuristique_simple()
        return 0

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        move = choice(moves) 
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")



