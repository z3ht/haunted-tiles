import numpy as np
from collections import deque


def dijkstras(board, start, destination=None):
    """
    :param board: current game board
    :param start: tuple start location
    :return:
    """
    moves = [[np.inf for i in range(7)] for j in range(7)]
    shortest_path = []
    visited = set()
    next_tiles = deque()
    valid_vertices = 0

    for y in range(7):
        for x in range(7):
            if board[y][x] > 1:
                valid_vertices += 1

    y, x = start
    moves[y][x] = 0

    while len(visited) < valid_vertices:
        for y_new, x_new in [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]:
            if _is_valid_move(y_new, x_new, board) and (y_new, x_new) not in visited:
                _parse_valid_neighbor(y, x, y_new, x_new, moves, next_tiles)
        visited.add((y, x))

        if (y, x) == destination:
            return moves, _shortest_path(moves, board, start, destination)

        y, x = next_tiles.popleft()
    return moves


def _is_valid_move(y_new, x_new, game_board):
    return y_new in range(0, 7) and x_new in range(0, 7) and game_board[y_new][x_new] > 1


def _parse_valid_neighbor(y, x, y_new, x_new, moves, next_tiles):
    next_tiles.append((y_new, x_new))
    moves_through_current = moves[y][x] + 1
    if moves_through_current < moves[y_new][x_new]:
        moves[y_new][x_new] = moves_through_current


def _shortest_path(moves, board, start, end):
    path = [end]
    while end != start:
        best_move = (0, 0)
        shortest_path = np.inf
        for y, x in [(end[0] - 1, end[1]), (end[0] + 1, end[1]), (end[0], end[1] - 1), (end[0], end[1] + 1)]:
            if _is_valid_move(y, x, board) and moves[y][x] < shortest_path:
                best_move = (y, x)
                shortest_path = moves[y][x]
        path.append(best_move)
        end = best_move
    return path

