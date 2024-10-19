from flask import Flask, render_template, request, redirect, session, flash
from db import batch_insert, get_data
from proses import preprocessing, predict_model
import os

app = Flask(__name__)
app.secret_key = 'KAMUJELEK'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.get('/')
def get_index():
    return redirect('/home')

@app.get('/home')
def get_home():
    if session.get('is_login'):
        return render_template('Home.html')
    else:
        return redirect("/login")

@app.post('/home')
def post_index():
    files = request.files['fileInput']
    df = preprocessing(files)
    insert_query = f"INSERT INTO sales (date, name, qty) VALUES (%s, %s, %s)"
    batch_insert(insert_query, df)
    prediction_model = predict_model(df)
    insert_query = f"INSERT INTO predict (date, name, qty) VALUES (%s, %s, %s)"
    batch_insert(insert_query, prediction_model)
    return redirect('/list')

@app.get('/algo')
def get_algo():
    if session.get('is_login'):
        return render_template('Algo.html')
    else:
        return redirect("/login")
    
@app.get('/list')
def get_list():
    if session.get('is_login'):
        res = get_data('sales', 7, 2023)
        return render_template('ListData.html', res=res)
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

# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)