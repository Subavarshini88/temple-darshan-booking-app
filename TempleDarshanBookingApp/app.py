from flask import Flask, render_template, request, redirect, session
from db import get_connection
import hashlib, random, string

app = Flask(__name__)
app.secret_key = "temple_secret_key"

# ---------- LOGIN ----------
@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/home')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,email,password) VALUES (%s,%s,%s)",
                    (username, email, password))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('login.html')

# ---------- HOME ----------
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM temples")
    temples = cur.fetchall()
    conn.close()
    return render_template('home.html', temples=temples)

# ---------- TEMPLE DETAIL ----------
@app.route('/temple/<temple_id>')
def temple(temple_id):
    if 'user_id' not in session:
        return redirect('/')
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM temples WHERE id=%s", (temple_id,))
    temple = cur.fetchone()
    conn.close()
    return render_template('temple.html', temple=temple)

# ---------- BOOKING ----------
@app.route('/booking', methods=['GET','POST'])
def booking():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        ref = 'TDB-2026-' + ''.join(random.choices(string.digits, k=5))
        prices = {'free':0, '300':300, '1000':1000, '5000':5000}
        dtype  = request.form.get('darshan_type','free')
        amount = prices.get(dtype, 0)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO bookings
            (user_id,temple_id,visit_date,slot,darshan_type,adults,children,amount,ref_number)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (session['user_id'],
             request.form.get('temple'),
             request.form.get('visit_date'),
             request.form.get('slot'),
             dtype,
             request.form.get('adults',1),
             request.form.get('children',0),
             amount, ref))
        conn.commit()
        conn.close()
        return render_template('booking.html', confirmed=True, ref=ref)
    return render_template('booking.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)