import random
import numpy as np
import time
import sys
import copy
import json
import gc
import subprocess

import Goban 
import gnugoPlayer
from io import StringIO


def add_to_json(board, result, file_name="tmp.json"):
    is_empty = False
    json_list = []
    read_file = open(file_name, "r")
    try:
        json_list = json.loads(read_file.read())
        print(len(json_list))
    except:
        is_empty = True
    read_file.close()
    if is_empty:
        data_to_json([board], [result], file_name)
    else:
        json_list.append({"in": board, "out": result})
        write_file = open(file_name, "w")
        json.dump(json_list, write_file)
        write_file.close()

def data_to_json(board_list, result_list, file_name="tmp.json"):
    json_list = []
    for i in range(len(board_list)):
        json_list.append({"in": board_list[i], "out": result_list[i]})
    write_file = open(file_name, "a")
    json.dump(json_list, write_file)
    write_file.close()

def board_to_goban_and_players(my_board):
    b = my_board["board"]
    g = Goban.Board()
    g._lastPlayerHasPassed = my_board["has_passed"]
    black_pos = []
    white_pos = []
    players = []
    player1 = gnugoPlayer.myPlayer()
    player1.newGame(Goban.Board._BLACK)
    players.append(player1)
    player2 = gnugoPlayer.myPlayer()
    player2.newGame(Goban.Board._WHITE)
    players.append(player2)
    def custom_play_move(pos):
        # print(pos)
        g.play_move(pos)
        player1._board.push(pos)
        player1._moves.playthis(Goban.Board.flat_to_name(pos))
        player2._board.push(pos)
        player2._moves.playthis(Goban.Board.flat_to_name(pos))
    for i in range(len(b)):
        for j in range(len(b[0])):
            if (b[i][j][0] == 1):
                black_pos.append(i + 9*j)
            if (b[i][j][1] == 1):
                white_pos.append(i + 9*j)
    if (my_board["to_move"] == Goban.Board._BLACK):
        while ((len(black_pos) > 0) or (len(white_pos) > 0)):
            if (len(black_pos) < len(white_pos)):
                custom_play_move(-1)
            else:
                custom_play_move(black_pos.pop())
            if (len(white_pos) < len(black_pos)+1):
                custom_play_move(-1)
            else:
                custom_play_move(white_pos.pop())
    else:
        while ((len(black_pos) > 1) or (len(white_pos) > 0)):
            if (len(black_pos) < len(white_pos)+1):
                custom_play_move(-1)
            else:
                custom_play_move(black_pos.pop())
            if (len(white_pos) < len(black_pos)):
                custom_play_move(-1)
            else:
                custom_play_move(white_pos.pop())
        custom_play_move(black_pos.pop())
    assert(len(black_pos) == 0)
    assert(len(white_pos) == 0)
    for p in players:
        p._board = copy.deepcopy(g)
    return (g, players)

def generate_single_board(nb_white, nb_black, to_move, has_passed=False):
    ret = {}
    # board = np.zeros((9,9,2))
    board = [[[0 for color in range(2)] for j in range(9)] for i in range(9)]
    for b in range(nb_black):
        pos = random.randint(0, 81-1-b)
        while ((board[pos%9][pos//9][0] != 0) or (board[pos%9][pos//9][1] != 0)):
            pos += 1
        board[pos%9][pos//9][0] = 1
    for w in range(nb_white):
        pos = random.randint(0, 81-nb_black-w)
        while ((board[pos%9][pos//9][0] != 0) or (board[pos%9][pos//9][1] != 0)):
            pos += 1
        board[pos%9][pos//9][1] = 1
    ret["board"] = board
    ret["to_move"] = to_move
    ret["has_passed"] = has_passed
    return ret

def generate_boards(n, nb_white=-1, nb_black=-1):
    assert(n > 0)
    if (nb_white == -1):
        nb_white = random.randint(3,70)
    if (nb_black == -1):
        nb_black = random.randint(3,70)
    ret = []
    for i in range(n):
        if (i%2 == 0):
            ret.append(generate_single_board(nb_white, nb_black, Goban.Board._BLACK, False))
        else:
            ret.append(generate_single_board(nb_white, nb_black, Goban.Board._WHITE, False))
        # ret.append(generate_single_board(nb_white, nb_black, Goban.Board._BLACK, True))
        # ret.append(generate_single_board(nb_white, nb_black, Goban.Board._WHITE, True))
    return ret

def generate_one_outcome(my_board):
    (b, players) = board_to_goban_and_players(my_board)
    color_to_move = my_board["to_move"]

    totalTime = [0,0] # total real time for each player
    nextplayercolor = color_to_move
    if (color_to_move == Goban.Board._BLACK):
        nextplayer = 0
    else:
        nextplayer = 1
    nbmoves = 1

    outputs = ["",""]
    sysstdout= sys.stdout
    stringio = StringIO()
    wrongmovefrom = 0

    sys.stdout = stringio
    while not b.is_game_over():
        # print("Referee Board:")
        # b.prettyPrint() 
        # print("Before move", nbmoves)
        legals = b.legal_moves() # legal moves are given as internal (flat) coordinates, not A1, A2, ...
        # print("Legal Moves: ", [b.move_to_str(m) for m in legals]) # I have to use this wrapper if I want to print them
        nbmoves += 1
        otherplayer = (nextplayer + 1) % 2
        othercolor = Goban.Board.flip(nextplayercolor)
        
        currentTime = time.time()
        # sys.stdout = stringio
        move = players[nextplayer].getPlayerMove() # The move must be given by "A1", ... "J8" string coordinates (not as an internal move)
        # sys.stdout = sysstdout
        playeroutput = stringio.getvalue()
        stringio.truncate(0)
        stringio.seek(0)
        # print(("[Player "+str(nextplayer) + "] ").join(playeroutput.splitlines(True)))
        outputs[nextplayer] += playeroutput
        totalTime[nextplayer] += time.time() - currentTime
        # print("Player ", nextplayercolor, players[nextplayer].getPlayerName(), "plays: " + move) #changed 
        if not Goban.Board.name_to_flat(move) in legals:
            # print(otherplayer, nextplayer, nextplayercolor)
            # print("Problem: illegal move")
            wrongmovefrom = nextplayercolor
            break
        b.push(Goban.Board.name_to_flat(move)) # Here I have to internally flatten the move to be able to check it.
        players[otherplayer].playOpponentMove(move)

        nextplayer = otherplayer
        nextplayercolor = othercolor
    # print("The game is over")
    result = b.result()
    sys.stdout = sysstdout

    # b.prettyPrint()
    # print("Time:", totalTime)
    # print("GO Score:", b.final_go_score())
    # print("Winner: ", end="")
    for p in players:
        p._gnugo._proc.terminate()
    if wrongmovefrom > 0:
        # b.prettyPrint()
        # sys.stderr.write(str(move))
        if wrongmovefrom == b._WHITE:
            # print("BLACK")
            sys.stderr.write(" : Coup invalide de la part du joueur blanc\n")
            return 1
        elif wrongmovefrom == b._BLACK:
            # print("WHITE")
            sys.stderr.write(" : Coup invalide de la part du joueur noir\n")
            return 0
        else:
            # print("ERROR")
            sys.stderr.write(" : Ne devrait jamais arriver...")
            # assert(False)
            return 0
    elif result == "1-0":
        # print("WHITE")
        return 0
    elif result == "0-1":
        # print("BLACK")
        return 1
    else:
        # print("DEUCE")
        return 0.5

def generate_black_win_probability(board, nb_games=1000):
    total_wins = 0
    i = 0
    nb_errors = 0
    while (i < nb_games):
        print(f"\rPartie {i+1}/{nb_games}", end="")
        try:
            total_wins += generate_one_outcome(board)
            i += 1
        except:
            nb_errors += 1
            sys.stderr.write(" : Erreur\n")
            time.sleep(1)
    sys.stderr.write(f"\r{nb_games} parties effectuées, {nb_errors} échec(s)\n")
    return total_wins/nb_games

def add_sample(output_file, nb_white, nb_black, to_move, has_passed=False, nb_games=1000):
    b = generate_single_board(nb_white, nb_black, to_move, has_passed)
    proba = generate_black_win_probability(b, nb_games)
    add_to_json(b, proba, output_file)


# boards = generate_boards(3, 5, 5)
# # g1 = board_to_goban(boards[0])
# # g2 = board_to_goban(boards[1])
# # g1.pretty_print()
# # g2.pretty_print()
# # print(generate_black_win_probability(boards[0], 10))

# probabilities = []
# # assert(False)
# for b in boards:
#     probabilities.append(generate_black_win_probability(b, 10))
# data_to_json(boards, probabilities)
games_per_board = 3
for i in range(3):
    add_sample("tmp.json", 5, 5, Goban.Board._BLACK, nb_games=games_per_board)
    add_sample("tmp.json", 5, 5, Goban.Board._WHITE, nb_games=games_per_board)