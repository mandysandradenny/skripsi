from flask import Flask, render_template, request, redirect, session, flash
from db import batch_insert, get_data
from proses import preprocessing, predict_model, create_chart, inventory_management, hashed, inventory_raw
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
        return render_template('Home.html', nav='home')
    else:
        return redirect("/login")

@app.post('/home')
def post_index():
    files = request.files['fileInput']
    df = preprocessing(files)
    insert_query = f"INSERT INTO sales (date, name, qty) VALUES (%s, %s, %s)"
    batch_insert(insert_query, df)
    prediction_model = predict_model(df)
    insert_query = f"INSERT INTO predict (month, name, qty) VALUES (%s, %s, %s)"
    batch_insert(insert_query, prediction_model)
    return redirect('/list')

@app.get('/algo')
def get_algo():
    if session.get('is_login'):
        return render_template('Algo.html', nav='algo')
    else:
        return redirect("/login")
    
@app.get('/list')
def get_list():
    if session.get('is_login'):
        res = get_data('sales')
        dates = get_data(query="SELECT DISTINCT DATE_FORMAT(date, '%Y-%m') AS month FROM sales;")
        return render_template('ListData.html', res=res, dates=dates, nav='list')
    else:
        return redirect("/login")

@app.get('/list/<year_month>')
def get_list_month(year_month):
    if session.get('is_login'):
        year, month = year_month.split("-")
        dates = get_data(query="SELECT DISTINCT DATE_FORMAT(date, '%Y-%m') AS month FROM sales;")
        res = get_data('sales', month, year)
        return render_template('ListData.html', res=res, dates=dates, nav='list', year_month=year_month)
    else:
        return redirect("/login")
    
@app.get('/pred')
def get_pred():
    if session.get('is_login'):
        dates = get_data(query="SELECT DISTINCT month FROM predict;")
        month = request.args.get('month')
        ukuran = request.args.get('ukuran')
        if month and not ukuran:
            name = get_data(query=f"SELECT DISTINCT name FROM predict WHERE month = '{month}'")
            data_all = get_data(query=f"SELECT name, qty FROM predict WHERE month = '{month}'")
            inventory = inventory_raw(data_all)
            return render_template('Prediksi.html', nav='pred', dates=dates, month=month, name=name, inventory=inventory)
        elif month and ukuran:
            return redirect(f"/pred/{month}/{ukuran}")
        return render_template('Prediksi.html', nav='pred', dates=dates, month=month)
    else:
        return redirect("/login")

@app.get('/pred/<month>/<ukuran>')
def get_pred_name(month, ukuran):
    if session.get('is_login'):
        data = get_data(query=f"SELECT qty FROM predict WHERE name = '{ukuran}' AND month = '{month}'")
        data_all = get_data(query=f"SELECT name, qty FROM predict WHERE name = '{ukuran}' AND month = '{month}'")
        qty_data = [x[0] for x in data]
        chart = None
        inventory = None
        if qty_data:
            chart = create_chart(ukuran, qty_data)
            inventory = inventory_management(data_all)

        return render_template('Ukuran.html', nav='pred', data=data, month=month, ukuran=ukuran, chart=chart, inventory_management=inventory)
    else:
        return redirect("/login")

@app.get('/login')
def get_login():
    return render_template("Login.html")

@app.post('/login')
def post_login():
    username = request.form['username']
    password = hashed(request.form['password'])
    data = get_data(query=f'SELECT username, password FROM user WHERE username = "{username}"')
    if data:
        mydata = data[0]
        if username == mydata[0] and password == mydata[1]:
            session['username'] = username
            session['is_login'] = True
            return redirect('/home')
    flash('Username atau Password Salah')
    return redirect("/login")

@app.get('/logout')
def logout():
    session.clear()
    return redirect("/login")

# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)