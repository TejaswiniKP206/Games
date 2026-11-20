from game import SnakeLadderGame

game = SnakeLadderGame(["Player 1", "Player 2"])

while game.winner is None:

    player = game.get_current_player()

    input(f"\n{player['name']}, press Enter to roll!")

    result = game.roll_dice()

    print("Dice:", result["dice"])
    print("Event:", result["message"])
    print("Position:", result["new_position"])

print("\nWinner:", game.winner)