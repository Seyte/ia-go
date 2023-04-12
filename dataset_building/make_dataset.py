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

def generate_single_board(nb_moves, to_move, has_passed=False):
    ret = {}
    b = Goban.Board()
    if (to_move == Goban.Board._WHITE):
        b.play_move(-1)
    for _ in range(nb_moves):
        to_move = random.choice(b.legal_moves())
        b.push(to_move)
        if b._gameOver:
            sys.stderr.write("Error (handled) : game already over\n")
            return generate_single_board(nb_moves, to_move, has_passed)
    arr = b._board
    board = [[[0 for color in range(2)] for j in range(9)] for i in range(9)]
    for i in range(9):
        for j in range(9):
            if (arr[i+9*j] == Goban.Board._BLACK):
                board[i][j][0] = 1
            if (arr[i+9*j] == Goban.Board._WHITE):
                board[i][j][1] = 1
    ret["board"] = board
    ret["to_move"] = to_move
    ret["has_passed"] = has_passed
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

def add_sample(output_file, nb_moves, to_move, has_passed=False, nb_games=1000):
    b = generate_single_board(nb_moves, to_move, has_passed)
    proba = generate_black_win_probability(b, nb_games)
    add_to_json(b, proba, output_file)

games_per_board = 1000
samples_per_nb_moves = 100
range_from = 0
range_to = 1
file = None

if (len(sys.argv)<4):
    print("Arguments missing, verify your command")
    print("Format : make_dataset.py <file> <nb_sample_per_it> <range_from> <range_to>")
    exit()
else:
    file = str(sys.argv[1])
    samples_per_nb_moves = int(sys.argv[2])
    range_from = int(sys.argv[3])
    range_to = int(sys.argv[4])


for nb_moves in range(range_from,range_to):
    for _ in range(samples_per_nb_moves):
        add_sample("tmp.json", nb_moves, Goban.Board._BLACK, nb_games=games_per_board)
        add_sample("tmp.json", nb_moves, Goban.Board._WHITE, nb_games=games_per_board)