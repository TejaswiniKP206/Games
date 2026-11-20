
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, join_room, emit
from game import SnakeLadderGame
import secrets

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)

socketio = SocketIO(app, cors_allowed_origins="*")

# Local game
current_game = None
game_mode = "local"

# Online rooms
rooms = {}


@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------------
# LOCAL GAME
# ----------------------------------

@app.route("/api/start", methods=["POST"])
def start_game():
    global current_game, game_mode

    data = request.get_json()
    game_mode = data.get("mode", "local")

    player1 = data.get("player1", "Player 1")
    player2 = data.get("player2", "Player 2")

    if game_mode == "computer":
        player2 = "Sunset Bot"

    current_game = SnakeLadderGame([player1, player2])

    return jsonify({
        "message": "Game started!",
        "status": current_game.get_status()
    })


@app.route("/api/roll", methods=["POST"])
def roll_dice():

    if current_game is None:
        return jsonify({"error": "Start a game first!"}), 400

    if current_game.winner:
        return jsonify({"error": "Game is over!"}), 400

    result = current_game.roll_dice()

    return jsonify({
        "result": result,
        "status": current_game.get_status()
    })


# ----------------------------------
# CREATE ONLINE ROOM
# ----------------------------------

@socketio.on("create_room")
def create_room(data):

    name = data.get("name", "Player 1").strip()[:15] or "Player 1"

    room_code = secrets.token_hex(3).upper()

    join_room(room_code)

    rooms[room_code] = {
        "players": [
            {
                "sid": request.sid,
                "name": name
            }
        ],
        "game": None
    }

    emit("room_created", {
        "room": room_code,
        "message": "Room created! Waiting for your friend..."
    }, to=request.sid)


# ----------------------------------
# JOIN ONLINE ROOM
# ----------------------------------

@socketio.on("join_room")
def join_game_room(data):

    room_code = data.get("room", "").strip().upper()
    name = data.get("name", "Player 2").strip()[:15] or "Player 2"

    room = rooms.get(room_code)

    if not room:
        emit("room_error", {"message": "Room not found!"})
        return

    if len(room["players"]) >= 2:
        emit("room_error", {"message": "Room is already full!"})
        return

    join_room(room_code)

    room["players"].append({
        "sid": request.sid,
        "name": name
    })

    names = [p["name"] for p in room["players"]]

    room["game"] = SnakeLadderGame(names)

    # Notify both players individually
    for index, player in enumerate(room["players"]):
        emit("game_started", {
            "room": room_code,
            "status": room["game"].get_status(),
            "player_index": index
        }, to=player["sid"])


# ----------------------------------
# ONLINE DICE ROLL
# ----------------------------------

@socketio.on("online_roll")
def online_roll(data):

    room_code = data.get("room", "").strip().upper()
    room = rooms.get(room_code)

    if not room or not room["game"]:
        emit("room_error", {"message": "Game room not available!"})
        return

    game = room["game"]

    player_index = game.current_player
    expected_sid = room["players"][player_index]["sid"]

    # Only the active player can roll
    if request.sid != expected_sid:
        emit("room_error", {"message": "Wait for your turn!"})
        return

    result = game.roll_dice()

    socketio.emit("online_update", {
        "result": result,
        "status": game.get_status()
    }, to=room_code)


# ----------------------------------
# DISCONNECT HANDLING
# ----------------------------------

@socketio.on("disconnect")
def handle_disconnect():

    for code, room in list(rooms.items()):

        for player in room["players"]:
            if player["sid"] == request.sid:

                socketio.emit("room_error", {
                    "message": "A player disconnected from the room."
                }, to=code)

                rooms.pop(code, None)
                return


if __name__ == "__main__":
    socketio.run(app, debug=True)
