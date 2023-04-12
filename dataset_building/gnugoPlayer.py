# -*- coding: utf-8 -*-

import time
import Goban 
from playerInterface import *
import GnuGo

def noprint(*args):
    pass

class myPlayer(PlayerInterface):
    ''' Antoher player example that simply act as a wrapper to my GnuGo.py interface. Allows to play against gnugo.'''

    def __init__(self):
        self._board = Goban.Board()
        self._gnugo = GnuGo.GnuGo(Goban.Board._BOARDSIZE)
        self._moves = self._gnugo.Moves(self._gnugo)
        self._mycolor = None

    def getPlayerName(self):
        return "Gnugo Player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            noprint("Referee told me to play but the game is over!")
            return "PASS" 
        # gets the legal moves from Goban (just to write them)
        board_moves = [Goban.Board.flat_to_name(m) for m in self._board.legal_moves()]
        noprint("Board Legal Moves for player " + Goban.Board.player_name(self._board._nextPlayer)) 
        (ok, legal) = self._gnugo.query("all_legal " + Goban.Board.player_name(self._board._nextPlayer))
        noprint("GNUGO Legal Moves are ", legal[1:])
        
        move = self._moves.get_randomized_best() 
        noprint("I am playing ", move) # New here: allows to consider internal representations of
        self._board.push(Goban.Board.name_to_flat(move))
        self._moves.playthis(move)
        #moves
        noprint("My current board :")
        self._board.prettyPrint()
        return move 

    def playOpponentMove(self, move):
        noprint("Opponent played ", move)
        self._board.push(Goban.Board.name_to_flat(move))
        self._moves.playthis(move)

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            noprint("I won!!!")
        else:
            noprint("I lost :(!!")



