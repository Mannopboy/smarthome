from flask import Flask, render_template, request
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
connections = []


@app.route('/')
def index():
    return render_template('index.html')


@sock.route('/echo')
def echo(sock):
    connections.append(sock)
    try:
        while True:
            data = sock.receive()
            print(f"Olingan xabar: {data}")
            # Broadcast to all other connections
            for connection in connections:
                if connection != sock:
                    connection.send(data)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connections.remove(sock)  # Clean up on disconnect


@app.route('/toggle')
def toggle():
    message = 1 if request.args.get('status') == 'on' else 0
    for connection in connections:
        try:
            print(message)
            connection.send(message)
        except Exception as e:
            print(f"Failed to send message to connection: {e}")
            connections.remove(connection)  # Clean up closed connection
    return 'Message sent', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
