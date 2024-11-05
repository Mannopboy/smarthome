from flask import Flask, render_template, request, jsonify
from flask_sock import Sock
from werkzeug.security import check_password_hash, generate_password_hash
import os
from sqlalchemy import Column, Integer, String, Boolean
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
sock = Sock(app)
connections = []
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123@localhost:5432/smart_home'
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/music_img'
app.config['SECRET_KEY'] = "_mmr_2007"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    admin = Column(Boolean)
    user = Column(Boolean, default=True)


rooms = {
    "mehmonxona": {"chiroq": False, "eshik": False},
    "oshxona": {"chiroq": False, "eshik": False},
    "garaj": {"chiroq": False, "eshik": False},
    "yotoqxona": {"chiroq": False, "eshik": False},
    "bolalar_xonasi": {"chiroq": False, "eshik": False},
    "vanna": {"chiroq": False, "eshik": False},
    "mehmonlar_yotoqxonasi": {"chiroq": False, "eshik": False},
    "omborxona": {"chiroq": False, "eshik": False},
    "basseyn": {"chiroq": False, "eshik": False},
    "uy_energiyasi": {"chiroq": False, "eshik": False},
    "konditsioner": {"chiroq": False, "eshik": False},
}


@app.route('/<room>/lamp', methods=['POST'])
def toggle_lamp(room):
    data = request.get_json()
    status = data.get("status")
    if room in rooms:
        rooms[room]["lamp"] = status
        return jsonify({"room": room, "lamp": rooms[room]["lamp"]})
    else:
        return jsonify({"error": "Xona topilmadi"}), 404


@app.route('/<room>/door', methods=['POST'])
def toggle_door(room):
    data = request.get_json()
    status = data.get("status")
    if room in rooms:
        rooms[room]["door"] = status
        return jsonify({"room": room, "door": rooms[room]["door"]})
    else:
        return jsonify({"error": "Xona topilmadi"}), 404


@app.route('/')
def index():
    return render_template('index.html')


@sock.route('/echo')
def echo(sock):
    connections.append(sock)
    while True:
        data = sock.receive()
        print(f"Olingan xabar: {data}")
        for connection in connections:
            connection.send(data)


@app.route('/toggle')
def toggle():
    message = 1 if request.args.get('status') == 'on' else 0
    for connection in connections:
        print(message)
        connection.send(message)
    return 'Message sent', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
