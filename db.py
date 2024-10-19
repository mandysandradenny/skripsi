import pymysql

def open_db():
    conn = pymysql.connect(
        host='localhost',
        db='skripsi',
        user='root',
        password=''
    )
    return conn

def connect(sql, operate='select', fetch='all'):
    conn = open_db()
    curs = conn.cursor()
    curs.execute(sql)
    if operate == 'select':
        if fetch == 'one':
            res = curs.fetchone()
        elif fetch == 'many':
            res = curs.fetchmany()
        else:
            res = curs.fetchall()
        curs.close()
        conn.close()
        return res
    else:
        conn.commit()
        curs.close()
        conn.close()

def batch_insert(sql, df):
    conn = open_db()
    curs = conn.cursor()
    for _, row in df.iterrows():
        curs.execute(sql, tuple(row))
    conn.commit()
    curs.close()
    conn.close()

def get_data(table, month=0, year=0):
    conn = open_db()
    curs = conn.cursor()
    if month and year:
        sql = f"SELECT date, name, qty FROM {table} WHERE EXTRACT(MONTH FROM date) = {month} AND EXTRACT(YEAR FROM date) = {year}"
    else:
        sql = f'SELECT date, name, qty FROM {table}'
    curs.execute(sql)
    res = curs.fetchall()
    curs.close()
    conn.close()
    return res