from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

# CORS 문제 방지
socketio = SocketIO(app, cors_allowed_origins="*")

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
    message = data["message"]
    nickname = data["nickname"]

    # 전체 채팅 전송
    emit("receive_message", data, broadcast=True)

    # 멘션 체크 (@닉네임)
    for sid, user_nickname in users.items():
        if f"@{user_nickname}" in message:
            emit("mention_alert", {
                "from": nickname,
                "message": message
            }, room=sid)


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)

