from flask import Flask, render_template

my_flask_app = Flask(__name__)


@my_flask_app.route('/')
def index():
    return render_template('index.html')


@my_flask_app.route('/cards/')
def all_cards():
    return render_template('all_cards.html')    


if __name__ == "__main__":
    my_flask_app.run(debug=True)