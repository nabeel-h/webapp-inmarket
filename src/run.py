from src.app import app

__author__ = "nblhn"

app.run(debug=app.config['DEBUG'], port=4990)