
import random

SNAKES = {
    27: 5,
    40: 18,
    43: 22,
    54: 34,
    76: 58,
    89: 68,
    99: 41
}

LADDERS = {
    4: 25,
    13: 46,
    33: 49,
    42: 63,
    50: 69,
    62: 81,
    74: 92
}


class SnakeLadderGame:

    def __init__(self, player_names):
        self.players = [
            {"name": name, "position": 0}
            for name in player_names
        ]

        self.current_player = 0
        self.winner = None
        self.history = []

        # Track consecutive sixes for each player
        self.six_counts = [0] * len(player_names)

    def roll_dice(self):

        if self.winner is not None:
            return {
                "message": "Game is already over!",
                "winner": self.winner
            }

        player_index = self.current_player
        player = self.players[player_index]

        dice = random.randint(1, 6)

        old_position = player["position"]
        new_position = old_position

        result = {
            "player": player["name"],
            "dice": dice,
            "old_position": old_position,
            "new_position": old_position,
            "event": "normal",
            "message": "",
            "extra_turn": False,
            "six_streak": 0
        }

        # ----------------------------------
        # CHECK CONSECUTIVE SIXES
        # ----------------------------------

        if dice == 6:
            self.six_counts[player_index] += 1
        else:
            self.six_counts[player_index] = 0

        result["six_streak"] = self.six_counts[player_index]

        # ----------------------------------
        # THREE CONSECUTIVE SIXES
        # ----------------------------------

        if self.six_counts[player_index] == 3:

            player["position"] = 0

            result["new_position"] = 0
            result["event"] = "three_sixes"
            result["message"] = (
                "Three consecutive sixes! "
                "Back to the starting point! 😵"
            )

            self.six_counts[player_index] = 0

            # Pass turn to the next player
            self.current_player = (
                self.current_player + 1
            ) % len(self.players)

        else:

            # ----------------------------------
            # NORMAL MOVEMENT
            # ----------------------------------

            new_position = old_position + dice

            if new_position > 100:

                result["event"] = "overshoot"
                result["message"] = (
                    "You need an exact roll to reach 100!"
                )

            else:

                player["position"] = new_position
                result["new_position"] = new_position

                # Check snake

                if new_position in SNAKES:

                    player["position"] = SNAKES[new_position]

                    result["new_position"] = player["position"]
                    result["event"] = "snake"
                    result["message"] = "Oh no! A snake! 🐍"

                # Check ladder

                elif new_position in LADDERS:

                    player["position"] = LADDERS[new_position]

                    result["new_position"] = player["position"]
                    result["event"] = "ladder"
                    result["message"] = "Yay! You climbed a ladder! 🪜"

                # Check winner

                if player["position"] == 100:

                    self.winner = player["name"]

                    result["event"] = "winner"
                    result["message"] = (
                        "Congratulations! You won! 🎉"
                    )

            # ----------------------------------
            # EXTRA TURN FOR SIX
            # ----------------------------------

            if self.winner is None:

                if dice == 6:

                    result["extra_turn"] = True
                    result["message"] += (
                        " You rolled a 6! Roll again! 🎲"
                    )

                else:

                    # Switch player after a non-six
                    self.current_player = (
                        self.current_player + 1
                    ) % len(self.players)

        # Save history
        self.history.append(result.copy())

        return result

    def get_current_player(self):
        return self.players[self.current_player]

    def get_status(self):

        return {
            "players": self.players,
            "current_player": self.current_player,
            "current_player_name": self.get_current_player()["name"],
            "winner": self.winner,
            "history": self.history,
            "snakes": SNAKES,
            "ladders": LADDERS,
            "six_counts": self.six_counts
        }


def computer_turn(game):
    return game.roll_dice()
