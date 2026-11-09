from flask import Flask

from config import configure_app
from routes.upload import register_routes


app = Flask(__name__)
configure_app(app)
register_routes(app)


if __name__ == "__main__":
    from routes.upload import get_local_ip

    print(f"Adres dla telefonu: http://{get_local_ip()}:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_debugger=False)
