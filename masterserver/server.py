from threading import Thread
from time import sleep, monotonic
from routes import endpoint
from routes.endpoint import serverList as sL
from flask import (
    Flask
)

app = Flask(__name__)
app.register_blueprint(endpoint.bp)

# TODO: Make more readable.
def routine():
    while True:
        sleep(6)
        for key, value in sL.copy().items():
            if monotonic() - value["keepAlive"] >= 15:
                sL.pop(key, None)

if __name__ == "__main__":
    task = Thread(target=routine, daemon=True)
    task.start()

    app.run() # debug=true makes the thread run twice... not issue for production