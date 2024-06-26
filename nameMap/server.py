from flask import Flask, render_template, request, url_for, redirect
from requestsIbge.ibgerequests import Ibge
from requestsIbge.database import DataIbge

# create a Flask app
app = Flask(__name__)

ibge = Ibge()


# create a index route
@app.route('/', methods=('GET', 'POST'))
def index():
    
    # create check 
    if request.method == 'POST':
        nome = request.form['nome']
        ibge.setName(nome)
        ibge.createFigAno(nome)
        return redirect(url_for(f'map', name = ibge.name))
    return render_template('create.html')

@app.route('/map/<name>')
def map(name):
    figure = ibge.cache.get(name)
    if figure:
        return render_template('teste.html', graphJSON=figure, name=name)
    else:
        return render_template('teste.html', graphJSON=ibge.fig_json, name=name)