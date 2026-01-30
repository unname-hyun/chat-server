from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)

users = {}  # socket id -> nickname

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("join")
def handle_join(data):
    nickname = data["nickname"]
    users[request.sid] = nickname
    emit(
        "system_message",
        f"{nickname} 님이 입장했습니다",
        broadcast=True
    )

@socketio.on("send_message")
def handle_message(data):
    emit("receive_message", data, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    nickname = users.get(request.sid)
    if nickname:
        emit(
            "system_message",
            f"{nickname} 님이 퇴장했습니다",
            broadcast=True
        )
        del users[request.sid]

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)

