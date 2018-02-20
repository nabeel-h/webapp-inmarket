__author__ = "nblhn"

from flask import Flask, render_template

import pygal

app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = "123"

@app.route('/')
def home():
    return render_template("home.jinja2")

"""
@app.route('/pygalexample')
def pygalexample():
    try:
        graph = pygal.XY(stroke=False, x_title='Customer Buy %', y_title='% of Total Sales')
        graph.title = 'Store Graph'
        graph.add('Drinking Stores', [
            {'value': (0.5,0.5), 'label':'Wendys'},
            {'value': (0.7,0.7),'label':"Subway"}
        ])
        #graph.add('Drug Stores', [(0.7143, 0.30), (0.45,0.21)])
        #graph.add('Eating Places', [(0.4582, 0.2199),(0.552, 0.34)])
        graph_data = graph.render_data_uri()
        return render_template("graphing.html", graph_data=graph_data)
    except Exception as e:
        return (str(e))
"""



from src.models.plots.views import plot_blueprint

app.register_blueprint(plot_blueprint, url_prefix="/create")
