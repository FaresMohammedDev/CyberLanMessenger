# -*- coding: utf-8 -*-
"""
CYBER-LAN GAMES ENGINE
Turn-based game state machines for:
1. Tic-Tac-Toe (X-O) [2 Players]
2. Snakes & Ladders (السلم والتعبان) [2 to 4+ Players]
Features: Turn synchronization, animated dice roll, winner detection,
and live Spectator broadcasting over LAN!
"""

import random
import time

# Standard Snakes & Ladders Board mappings (1 to 100)
LADDERS = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
SNAKES = {17: 7, 54: 34, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}


class TicTacToeGame:
    def __init__(self, game_id, player_x_ip, player_x_nick, player_o_ip, player_o_nick):
        self.game_id = game_id
        self.player_x = {"ip": player_x_ip, "nick": player_x_nick}
        self.player_o = {"ip": player_o_ip, "nick": player_o_nick}
        self.board = [" "] * 9
        self.current_turn = "X"
        self.winner = None
        self.winning_line = None
        self.history = []

    def make_move(self, index, player_symbol):
        if self.winner is not None or self.board[index] != " ":
            return False, "Invalid move"
        if player_symbol != self.current_turn:
            return False, "Not your turn"

        self.board[index] = player_symbol
        self.history.append((index, player_symbol))

        # Check win
        win_combos = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # Cols
            (0, 4, 8), (2, 4, 6)             # Diagonals
        ]
        for a, b, c in win_combos:
            if self.board[a] != " " and self.board[a] == self.board[b] == self.board[c]:
                self.winner = player_symbol
                self.winning_line = (a, b, c)
                return True, f"Player {player_symbol} Wins!"

        # Check Draw
        if " " not in self.board:
            self.winner = "DRAW"
            return True, "Draw Game!"

        # Switch Turn
        self.current_turn = "O" if self.current_turn == "X" else "X"
        return True, "Turn passed"

    def to_dict(self):
        return {
            "game_type": "XO",
            "game_id": self.game_id,
            "player_x": self.player_x,
            "player_o": self.player_o,
            "board": self.board,
            "current_turn": self.current_turn,
            "winner": self.winner,
            "winning_line": self.winning_line
        }


class SnakesLaddersGame:
    def __init__(self, game_id, players_list):
        """
        players_list = [{"ip": ..., "nick": ..., "color": ...}, ...]
        """
        self.game_id = game_id
        self.players = players_list # 2 to 4+
        self.positions = {p["ip"]: 1 for p in players_list}
        self.current_player_idx = 0
        self.last_roll = None
        self.last_event_msg = "Game started! Waiting for first roll."
        self.winner = None

    def roll_dice(self, player_ip):
        if self.winner is not None:
            return False, "Game has already concluded"

        curr_p = self.players[self.current_player_idx]
        if curr_p["ip"] != player_ip:
            return False, f"Not your turn! It's {curr_p['nick']}'s turn."

        roll = random.randint(1, 6)
        self.last_roll = roll
        pos = self.positions[player_ip]
        new_pos = pos + roll

        event = f"{curr_p['nick']} rolled a {roll}!"

        if new_pos > 100:
            event += " (Bounced! Need exact roll to reach 100)."
        elif new_pos == 100:
            self.positions[player_ip] = 100
            self.winner = curr_p
            event += f" 🏆 {curr_p['nick']} REACHED 100 AND WINS THE GAME!"
            self.last_event_msg = event
            return True, event
        else:
            # Check ladders
            if new_pos in LADDERS:
                climbed = LADDERS[new_pos]
                event += f" 🪜 LADDER CLIMBED! from {new_pos} up to {climbed}!"
                new_pos = climbed
            # Check snakes
            elif new_pos in SNAKES:
                bitten = SNAKES[new_pos]
                event += f" 🐍 SNAKE BITE! slid down from {new_pos} to {bitten}!"
                new_pos = bitten
            else:
                event += f" Moved to square {new_pos}."

            self.positions[player_ip] = new_pos

        self.last_event_msg = event

        # Advance turn unless rolled a 6 (bonus turn!)
        if roll != 6 or self.winner is not None:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        else:
            self.last_event_msg += " (Rolled a 6! Extra roll granted)."

        return True, event

    def to_dict(self):
        return {
            "game_type": "SNAKES",
            "game_id": self.game_id,
            "players": self.players,
            "positions": self.positions,
            "current_player_idx": self.current_player_idx,
            "last_roll": self.last_roll,
            "last_event_msg": self.last_event_msg,
            "winner": self.winner
        }


if __name__ == "__main__":
    p = [{"ip": "192.168.20.54", "nick": "Neo", "color": "#00ff66"},
         {"ip": "192.168.20.53", "nick": "Phantom", "color": "#00f0ff"}]
    snk = SnakesLaddersGame("test_game", p)
    ok, msg = snk.roll_dice("192.168.20.54")
    print(msg)
    print(snk.to_dict())
