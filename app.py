from flask import Flask, render_template, request, redirect, session, flash
from db import connect, open_db, batch_insert
from preprocess import preprocessing
from keras.models import load_model
import os

app = Flask(__name__)
app.secret_key = 'kamujelek'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

modelPath = 'checkpoint.weights.h5'
model = load_model(modelPath)

@app.get('/')
def get_index():
    return redirect('/home')
    # res = connect("SELECT * FROM sales;")
    # return render_template('index.html', res=res)

@app.get('/home')
def get_home():
    if session.get('is_login'):
        return render_template('Home.html')
    else:
        return redirect("/login")

@app.get('/algo')
def get_algo():
    if session.get('is_login'):
        return render_template('Algo.html')
    else:
        return redirect("/login")
    
@app.get('/list')
def get_list():
    if session.get('is_login'):
        return render_template('ListData.html')
    else:
        return redirect("/login")
    
@app.get('/pred')
def get_pred():
    if session.get('is_login'):
        return render_template('Prediksi.html')
    else:
        return redirect("/login")

@app.get('/login')
def get_login():
        return render_template("Login.html")

@app.post('/login')
def post_login():
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['is_login'] = True
            return redirect('/home')
        else:
            flash('Login Gagal')
            return redirect("/login")

@app.get('/logout')
def logout():
        session.clear()
        return redirect("/login")
    
@app.post('/')
def post_index():
    files = request.files['xlsx']
    df = preprocessing(files)
    insert_query = f"INSERT INTO sales (date, name, qty) VALUES (%s, %s, %s)"
    batch_insert(insert_query, df)
    return redirect('/')

# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)