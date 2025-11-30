from flask import Flask, render_template, request, redirect
import sqlite3
import csv

app = Flask(__name__)
DATABASE = 'shoes.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS shoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            price REAL,
            experience TEXT,
            weight REAL
        )
    ''')
    conn.commit()
    conn.close()


def load_csv():
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM shoes').fetchone()[0]
    
    if count == 0:
        with open('BrooksShoes.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                weight = float(row['Weight(g)']) if row['Weight(g)'] else 0
                conn.execute(
                    'INSERT INTO shoes (name, type, price, experience, weight) VALUES (?,?,?,?,?)',
                    (row['Name'], row['Type'], float(row['Price']), row['Experience'], weight)
                )
        conn.commit()
    conn.close()


# 메인 페이지 (검색 + 목록)
@app.route('/')
def index():
    keyword = request.args.get('keyword', '')
    conn = get_db()
    
    if keyword:
        shoes = conn.execute(
            'SELECT * FROM shoes WHERE name LIKE ? OR experience LIKE ? ORDER BY name',
            ('%'+keyword+'%', '%'+keyword+'%')
        ).fetchall()
    else:
        shoes = conn.execute('SELECT * FROM shoes ORDER BY name').fetchall()
    
    conn.close()
    return render_template('base.html', shoes=shoes, keyword=keyword)


# 추가
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = get_db()
        conn.execute(
            'INSERT INTO shoes (name, type, price, experience, weight) VALUES (?,?,?,?,?)',
            (request.form['name'], request.form['type'], request.form['price'], 
             request.form['experience'], request.form['weight'])
        )
        conn.commit()
        conn.close()
        return redirect('/')
    
    return render_template('add.html')


# 수정
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    
    if request.method == 'POST':
        conn.execute(
            'UPDATE shoes SET name=?, type=?, price=?, experience=?, weight=? WHERE id=?',
            (request.form['name'], request.form['type'], request.form['price'],
             request.form['experience'], request.form['weight'], id)
        )
        conn.commit()
        conn.close()
        return redirect('/')
    
    shoe = conn.execute('SELECT * FROM shoes WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('edit.html', shoe=shoe)


# 삭제
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM shoes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    init_db()
    load_csv()
    app.run(debug=True)