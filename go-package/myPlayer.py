import time
import Goban 
from random import choice, randint
from playerInterface import *
import signal
import copy 
import enum
from tensorflow.keras.models import load_model
import numpy as np
import os

class myPlayer(PlayerInterface):
    MAX_VALUE = 10000

    class Strategy_Phase(enum.Enum):
        First_Phase = 1
        Early_Game_Phase = 2
        MinMax_Phase = 3

    def heuristic(self,board):
        sigset = signal.sigset_t()
        sigset.add(signal.SIGALRM)
        oldset = signal.sigprocmask(signal.SIG_BLOCK, sigset)
        if board.is_game_over():
            return self.getWinnerColor(board)
        print(board.get_board().shape)
        input_data = board.get_board()
        board_to_predict = np.zeros((11, 11, 2))
        for x in range (9):
            for y in range (9):
                if input_data[x+y*9]==board._BLACK:
                    board_to_predict[x+1][y+1][0] = 1
                elif input_data[x+y*9]==board._WHITE:
                    board_to_predict[x+1][y+1][1] = 1
        board_to_predict = np.expand_dims(board_to_predict, axis=0)
        value = None
        if (self._mycolor == Goban.Board._BLACK):
            value = self._model.predict(board_to_predict)[0][0]
        else :
            value = self._model.predict(board_to_predict)[0][1]
        signal.sigprocmask(signal.SIG_SETMASK, oldset)
        return value
    
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._last_best_move = None
        self._play_time = 1 # to cover additional time we can't mesure.
        self._phase = self.Strategy_Phase.First_Phase # TODO : change this
        self._model = load_model("my_model") # load Keras model
        self._pid = os.getpid()

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
    
    def get_moves_from_center(self, x):
        assert(x >= 0)
        moves = self._board.generate_legal_moves()
        if (x >= 4):
            return moves
        lines = ["A", "B", "C", "D", "E", "F", "G", "H", "J"]
        for i in range(9):
            for j in range(4-x):
                to_be_removed = [j + 9*(i+1),
                                 (8-j) + 9*(i+1),
                                 i + 9*j,
                                 i + 9*(8-j)]
                for m in to_be_removed:
                    if m in moves:
                        moves.remove(m)
        return moves
    
    def getPlayerName(self):
        return "MinimaxPlayer"
        
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
    
    def playFirstPhase(self):
        assert(self._mycolor != None)
        moves_history = self._board._historyMoveNames
        match self._mycolor:
            case Goban.Board._BLACK:
                match self._board._nbBLACK:
                    case 0:
                        self._phase = self.Strategy_Phase.Early_Game_Phase
                        return "E5"
                    case _:
                        self._phase = self.Strategy_Phase.Early_Game_Phase
                        return "PASS"
            case Goban.Board._WHITE:
                match self._board._nbWHITE:
                    case 0:
                        self._phase = self.Strategy_Phase.Early_Game_Phase
                        match moves_history[0]:
                            # au centre
                            case "E5":
                                return "G5"
                            # en diagonale en partant du centre
                            case "D4" | "C3":
                                return "F6"
                            case "F4" | "G3":
                                return "D6"
                            case "D6" | "C7":
                                return "F4"
                            case "F6" | "G7":
                                return "D4"
                            # en ligne droite ou en L en partant du centre
                            case "D3" | "E3" | "F3" | "E4":
                                return "E6"
                            case "G4" | "G5" | "G6" | "F5":
                                return "D5"
                            case "D7" | "E7" | "F7" | "E6":
                                return "E4"
                            case "C4" | "C5" | "C6" | "D5":
                                return "F5"
                            # si le premier joueur n'a pas joué dans la zone centrale
                            case _:
                                return "E5"
                    case _:
                        self._phase = self.Strategy_Phase.Early_Game_Phase
                        return "PASS"
            case _: #shouldn't go in there. fallback.
                return 0
        return "PASS"

    def getPlayerMove(self):
        if (self._phase == self.Strategy_Phase.First_Phase):
            best_move = self.playFirstPhase()
            self._board.push(Goban.Board.name_to_flat(best_move))
            return best_move
        else:
            currentTime = time.time()
            if self._board.is_game_over():
                print("Referee told me to play but the game is over!")
                return "PASS" 
            
            if (self._phase == self.Strategy_Phase.Early_Game_Phase):
                moves = self.get_moves_from_center(2)
                if (len(moves) <= 17):
                    self._phase = self.Strategy_Phase.MinMax_Phase
            elif (self._phase == self.Strategy_Phase.MinMax_Phase):
                moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
            self._last_best_move = choice(moves) 
            max_depth = 1
            try :
                signal.signal(signal.SIGALRM, self.handler)
                signal.alarm(self.getRoundTime())
                print("I'll have ",self.getRoundTime())
                while(True):
                    self._last_best_move = self.start_deep(copy.deepcopy(self._board),0,max_depth)
                    max_depth+=1
            except TimeoutError:
                print("End of time ! Returning my best move.")
                pass # if we do not use iterative deepening.
            finally:
                signal.alarm(0)
                print("I got to explore until " + str(max_depth-1))
                self._board.push(self._last_best_move)
                # Deepcopy allows to consider internal representations of moves
                print("I am playing ", self._board.move_to_str(self._last_best_move))
                print("My current board :")
                self._board.prettyPrint()
                self._play_time += time.time() - currentTime
                print("Player time = " + str(self._play_time))
                return Goban.Board.flat_to_name(self._last_best_move) 

    def playOpponentMove(self, move):
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("Minimax : I won!!!")
        else:
            print("Minimax : I lost :(!!")