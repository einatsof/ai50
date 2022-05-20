"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_cells = sum(row.count(X) for row in board)
    o_cells = sum(row.count(O) for row in board)
    if x_cells == o_cells:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                possible_actions.add((i, j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] is not EMPTY:
        raise ValueError("Action %s in not valid - cell is not empty" % (action,))
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    all_rows = []
    # Add rows
    for row in board:
        all_rows.append(row)
    # Add columns
    columns = [[board[j][i] for j in range(3)] for i in range(3)]
    for row in columns:
        all_rows.append(row)
    # Add diagonals
    all_rows.append([board[0][0], board[1][1], board[2][2]])
    all_rows.append([board[0][2], board[1][1], board[2][0]])
    # Check all possible rows
    for row in all_rows:
        if row.count(X) == 3:
            return X
        elif row.count(O) == 3:
            return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    for row in board:
        for cell in row:
            if cell is EMPTY:
                # Empty cell found - game not over
                return False
    # Game is tied
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    the_winner = winner(board)
    if the_winner is X:
        return 1
    elif the_winner is O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    current_player = player(board)
    possible_actions = []
    alpha = -math.inf
    beta = math.inf
    for action in actions(board):
        if current_player is X:
            possible_actions.append((min_value(result(board, action), alpha, beta), action))
        else:
            possible_actions.append((max_value(result(board, action), alpha, beta), action))
    if current_player is X:
        possible_actions.sort(key=lambda x: x[0], reverse=True)
    else:
        possible_actions.sort(key=lambda x: x[0])
    return possible_actions[0][1]


def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board)
    value = math.inf
    for action in actions(board):
        value = min(value, max_value(result(board, action), alpha, beta))
        beta = min(beta, value)
        if beta <= alpha:
            break
    return value


def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board)
    value = -math.inf
    for action in actions(board):
        value = max(value, min_value(result(board, action), alpha, beta))
        alpha = max(alpha, value)
        if beta <= alpha:
            break
    return value
