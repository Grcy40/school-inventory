from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
DATABASE = 'inventory.db'
EXCEL_FILE = 'inventory(1).xlsx'


def init_db_from_excel():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create table if not exists
    c.execute('''
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

    # Check if table is empty
    c.execute('SELECT COUNT(*) FROM equipment')
    if c.fetchone()[0] == 0 and os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
            expected_cols = {'model', 'mac_address', 'owner', 'supplier', 'supplier_date',
                             'warranty', 'lpo_number', 'status', 'specifications'}
            if expected_cols.issubset(set(df.columns)):
                df.to_sql('equipment', conn, if_exists='append', index=False)
                print("✅ Data imported from Excel.")
            else:
                print(f"⚠️ Missing columns: {expected_cols - set(df.columns)}")
        except Exception as e:
            print(f"❌ Excel import failed: {e}")
    conn.commit()
    conn.close()


init_db_from_excel()


@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    items = conn.execute('SELECT * FROM equipment').fetchall()
    conn.close()
    return render_template('index.html', items=items)


@app.route('/add', methods=['GET', 'POST'])
def add():
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
        conn = sqlite3.connect(DATABASE)
        conn.execute('''
            INSERT INTO equipment (
                model, mac_address, owner, supplier, supplier_date,
                warranty, lpo_number, status, specifications
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    item = conn.execute('SELECT * FROM equipment WHERE id = ?', (id,)).fetchone()

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
        conn.execute('''
            UPDATE equipment SET
                model = ?, mac_address = ?, owner = ?, supplier = ?, supplier_date = ?,
                warranty = ?, lpo_number = ?, status = ?, specifications = ?
            WHERE id = ?
        ''', data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', item=item)


@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect(DATABASE)
    conn.execute('DELETE FROM equipment WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                expected = {'model', 'mac_address', 'owner', 'supplier', 'supplier_date',
                            'warranty', 'lpo_number', 'status', 'specifications'}
                if expected.issubset(set(df.columns)):
                    conn = sqlite3.connect(DATABASE)
                    df.to_sql('equipment', conn, if_exists='append', index=False)
                    conn.close()
                    return redirect(url_for('index'))
                else:
                    return "Missing columns in Excel file.", 400
            except Exception as e:
                return f"Error reading file: {e}", 500
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
