from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3


app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('staff.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
def index():
    conn = get_db_connection()
    staff = conn.execute('SELECT * FROM staff').fetchall()
    conn.close()
    return render_template('index.html', staff=staff)

@app.route('/add_staff', methods=['POST'])
def add_staff():
    ign = request.form['ign']
    rank = request.form['rank']

    conn = get_db_connection()
    conn.execute("INSERT INTO staff (ign, rank, Creation_Date, Last_Promotion_Date) VALUES (?, ?, datetime('now'), datetime('now'))", (ign, rank))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))
@app.route('/promote_staff', methods=['POST'])
def promote_staff_member():
    staff_id = request.form['id']

    conn = get_db_connection()
    staff_member = conn.execute('SELECT * FROM staff WHERE id = ?', (staff_id,)).fetchone()
    current_rank = staff_member['rank']

    if current_rank == "Trial Mod":
        new_rank = "Mod"
    elif current_rank == "Mod":
        new_rank = "Mod+"
    elif current_rank == "Mod+":
        new_rank = "Sr. Mod"
    elif current_rank == "Sr. Mod":
        new_rank = "Jr. Admin"
    elif current_rank == "Jr. Admin":
        new_rank = "Admin"
    elif current_rank == "Admin":
        new_rank = "Sr. Admin"
    else:
        new_rank = current_rank

    conn.execute("UPDATE staff SET rank = ?, Last_Promotion_Date = datetime('now') WHERE id = ?", (new_rank, staff_id))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/promote/<int:staff_id>', methods=['POST'])
def promote_staff(staff_id):
    rank = request.form['rank']
    last_promotion = request.form['last_promotion']
    conn = sqlite3.connect('staff.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE staff SET rank = ?, Last_Promotion_Date = ? WHERE id = ?", (rank, last_promotion, staff_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)

@app.route('/demote_staff', methods=['POST'])
def demote_staff():
    staff_id = request.form['id']

    conn = get_db_connection()
    staff_member = conn.execute('SELECT * FROM staff WHERE id = ?', (staff_id,)).fetchone()
    current_rank = staff_member['rank']

    if current_rank == "Sr. Admin":
        new_rank = "Admin"
    elif current_rank == "Admin":
        new_rank = "Jr. Admin"
    elif current_rank == "Jr. Admin":
        new_rank = "Sr. Mod"
    elif current_rank == "Sr. Mod":
        new_rank = "Mod+"
    elif current_rank == "Mod+":
        new_rank = "Mod"
    elif current_rank == "Mod":
        new_rank = "Trial Mod"
    else:
        new_rank = current_rank

    conn.execute("UPDATE staff SET rank = ?, Last_Promotion_Date = datetime('now') WHERE id = ?", (new_rank, staff_id))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/delete_staff', methods=['POST'])
def delete_staff():
    staff_id = request.form['id']

    conn = get_db_connection()
    conn.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

def update_last_promotion():
    staff_id = request.form['id']
    last_promotion_date = request.form['date']

    conn = sqlite3.connect('staff.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE staff SET Last_Promotion_Date = ? WHERE id = ?', (last_promotion_date, staff_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)

    
