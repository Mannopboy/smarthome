from flask import Flask, render_template, request, jsonify, session, or_, redirect, url_for
from flask_sock import Sock
from werkzeug.security import check_password_hash, generate_password_hash
import os
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
sock = Sock(app)
connections = []
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/smart_home'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['SECRET_KEY'] = "_mmr_2007"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    password = Column(String)
    username = Column(String, default=True)
    homes = db.relationship("Home", backref="user", order_by="Home.id")


class Home(db.Model):
    __tablename__ = "home"
    id = Column(Integer, primary_key=True)
    number = Column(String)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    rooms = db.relationship("Room", backref="home", order_by="Room.id")


class Room(db.Model):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    home_id = Column(Integer, ForeignKey('home.id'))
    items = db.relationship("Item", backref="room", order_by="Item.id")


class Item(db.Model):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Boolean)
    room_id = Column(Integer, ForeignKey('room.id'))


def get_current_user():
    user_result = None
    if "username" in session:
        user_result = User.query.filter(User.username == session['username']).first()
    return user_result


@app.route('/logout')
def logout():
    session['id'] = None
    session['username'] = None
    return redirect(url_for('login'))


rooms = {
    "living_room": {"lamp": False, "door": False},
    "kitchen": {"lamp": False, "door": False},
    "garage": {"lamp": False, "door": False},
    "bedroom": {"lamp": False, "door": False},
    "children_room": {"lamp": False, "door": False},
    "bathroom": {"lamp": False, "door": False},
    "guest_bedroom": {"lamp": False, "door": False},
    "storage_room": {"lamp": False, "door": False},
    "swimming_pool": {"lamp": False, "door": False},
    "house_energy": {"lamp": False, "door": False},
    "air_conditioner": {"lamp": False, "door": False},
}

items = [{"lamp": False}, {"door": False}]


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        date = request.get_json()
        print(date)
        username = request.get_json()['username']
        password = request.get_json()['password']
        get_user = User.query.filter(User.username == username).first()
        if get_user:
            checked = check_password_hash(get_user.password, password)
            session['id'] = get_user.id
            session['username'] = username
            if checked:
                return jsonify({
                    'status': True
                })
            else:
                return jsonify({
                    'status': False
                })
    else:
        return jsonify({'status': False
                        })


@app.route('/rooms')
def rooms():
    user = User.query.filter(User.id == session['id']).first()
    if user:
        rooms = Home.query.filter(Home.user_id == user.id).first().rooms
        list = []
        for room_l in rooms:
            list.append({
                'room': room_l.name
            })
        return jsonify({
            'rooms': list
        })


@app.route('/')
def index():
    user = User.query.filter(User.id == 1).first()
    if not user:
        name = 'user 1'
        surname = 'user 1'
        username = 'admin'
        password = '123'
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        add = User(name=name, surname=surname, password=hashed_password, username=username)
        db.session.add(add)
        db.session.commit()
    home = Home.query.filter(Home.id == 1).first()
    if not home:
        add = Home(number='a1', name='Home 1', user_id=user.id)
        db.session.add(add)
        db.session.commit()
    for room, keys in rooms.items():
        room = Room.query.filter(Room.name == room, Room.home_id == home.id).first()
        if not room:
            add = Room(name=room, home_id=home.id)
            db.session.add(add)
            db.session.commit()
    rooms_b = Room.query.filter(Room.home_id == home.id).order_by(Room.id).all()
    for rome in rooms_b:
        for item in items:
            for item, keys in item.items():
                item_n = Item.query.filter(Item.room_id == rome.id, Room.name == item).first()
                if not item_n:
                    add = Item(room_id=rome.id, name=item, status=keys)
                    db.session.add(add)
                    db.session.commit()
    return render_template('index.html')


@app.route('/room/<int:room>', methods=['GET'])
def room(room):
    room_d = Room.query.filter(Room.id == room).first().items
    list = []
    for item in room_d:
        list.append({
            'name': item.name,
            'status': item.status
        })
    return jsonify({'items': list})


@app.route('/<room>/lamp', methods=['POST'])
def toggle_lamp(room):
    data = request.get_json()
    status = data.get("status")
    room_d = Room.query.filter(Room.id == room).first()
    item = Item.query.filter(Item.room_id == room_d.id, Item.name == 'lamp').first()
    if item:
        item.status = status
        db.session.commit()
        return jsonify({"lamp": status})
    else:
        return jsonify({"error": "Xona topilmadi"}), 404


@app.route('/<room>/door', methods=['POST'])
def toggle_door(room):
    data = request.get_json()
    status = data.get("status")
    room_d = Room.query.filter(Room.id == room).first()
    item = Item.query.filter(Item.room_id == room_d.id, Item.name == 'door').first()
    if item:
        item.status = status
        db.session.commit()
        return jsonify({"door": status})
    else:
        return jsonify({"error": "Xona topilmadi"}), 404


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
        try:
            print(message)
            connection.send(message)
        except Exception as e:
            print(f"Failed to send message to connection: {e}")
            connections.remove(connection)
    return 'Message sent', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
