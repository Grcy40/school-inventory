from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import sqlite3

# ✅ Initialize Flask app
app = Flask(__name__, template_folder='templates')

# ✅ SQLite database file
DATABASE = 'inventory.db'

# ✅ Ensure database table exists
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT,
                mac_address TEXT,
                owner TEXT,
                supplier TEXT,
                supplier_date TEXT,
                warranty TEXT,
                lpo_number TEXT,
                status TEXT,
                specifications TEXT
            )
        ''')
init_db()

# ✅ Home page route
@app.route('/')
def index():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM equipment')
        equipment = cursor.fetchall()
    return render_template('index.html', equipment=equipment)

# ✅ Add new equipment
@app.route('/add', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        data = (
            request.form['model'],
            request.form['mac_address'],
            request.form['owner'],
            request.form['supplier'],
            request.form['supplier_date'],
            request.form['warranty'],
            request.form['lpo_number'],
            request.form['status'],
            request.form['specifications']
        )
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                INSERT INTO equipment (
                    model, mac_address, owner, supplier,
                    supplier_date, warranty, lpo_number, status, specifications
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
        return redirect(url_for('index'))
    return render_template('add.html')

# ✅ Edit equipment
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_equipment(id):
    if request.method == 'POST':
        data = (
            request.form['model'],
            request.form['mac_address'],
            request.form['owner'],
            request.form['supplier'],
            request.form['supplier_date'],
            request.form['warranty'],
            request.form['lpo_number'],
            request.form['status'],
            request.form['specifications'],
            id
        )
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                UPDATE equipment SET
                    model=?, mac_address=?, owner=?, supplier=?,
                    supplier_date=?, warranty=?, lpo_number=?, status=?, specifications=?
                WHERE id=?
            ''', data)
        return redirect(url_for('index'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM equipment WHERE id=?', (id,))
        item = cursor.fetchone()
    return render_template('edit.html', item=item)

# ✅ Delete equipment
@app.route('/delete/<int:id>')
def delete_equipment(id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DELETE FROM equipment WHERE id=?', (id,))
    return redirect(url_for('index'))

# ✅ Upload Excel
@app.route('/upload', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl')
            expected_columns = [
                'model', 'mac_address', 'owner', 'supplier',
                'supplier_date', 'warranty', 'lpo_number', 'status', 'specifications'
            ]
            if set(df.columns) >= set(expected_columns):
                with sqlite3.connect(DATABASE) as conn:
                    for _, row in df.iterrows():
                        data_tuple = tuple(row[col] for col in expected_columns)
                        conn.execute('''
                            INSERT INTO equipment (
                                model, mac_address, owner, supplier,
                                supplier_date, warranty, lpo_number, status, specifications
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', data_tuple)
                return redirect(url_for('index'))
            else:
                return "Excel file missing required columns", 400
    return render_template('upload.html')

# ✅ Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # ✅ Needed for Render
    app.run(host='0.0.0.0', port=port, debug=True)

