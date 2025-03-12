from flask import Flask
from lock import lock_blueprint

app = Flask(__name__)

# Register the Lock Control Blueprint
app.register_blueprint(lock_blueprint, url_prefix="/lock")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
