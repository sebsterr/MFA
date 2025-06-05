from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pyotp
import qrcode
import io
import base64
import os
import random

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # înlocuiește cu ceva mai sigur
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# === MODEL UTILIZATOR ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
    otp_secret = db.Column(db.String(16))
    recovery_codes = db.Column(db.Text)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# === HELPER: Coduri de backup ===
def generate_recovery_codes():
    return ','.join([str(random.randint(100000, 999999)) for _ in range(5)])


# === RUTE ===
@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "Username already exists"

        otp_secret = pyotp.random_base32()
        recovery = generate_recovery_codes()

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password_hash=hashed,
                    otp_secret=otp_secret, recovery_codes=recovery)
        db.session.add(user)
        db.session.commit()

        session['username'] = username
        return redirect('/2fa-setup')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect('/2fa')
        return "Login failed"
    return render_template('login.html')


@app.route('/2fa-setup')
def twofa_setup():
    user = User.query.filter_by(username=session['username']).first()
    uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(name=user.username, issuer_name="2FA Demo Site")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('two_factor.html', img_b64=img_b64, setup=True)


@app.route('/2fa', methods=['GET', 'POST'])
def twofa_verify():
    user = User.query.filter_by(username=session['username']).first()
    totp = pyotp.TOTP(user.otp_secret)

    if request.method == 'POST':
        code = request.form['token']
        recovery = request.form.get('recovery', '').strip()

        if totp.verify(code):
            session['authenticated'] = True
            return redirect('/dashboard')
        elif recovery and recovery in user.recovery_codes.split(','):
            # remove used recovery code
            codes = user.recovery_codes.split(',')
            codes.remove(recovery)
            user.recovery_codes = ','.join(codes)
            db.session.commit()
            session['authenticated'] = True
            return redirect('/dashboard')
        else:
            return "Invalid code or recovery code"
    return render_template('two_factor.html', setup=False)


@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect('/login')
    return render_template('dashboard.html')


@app.route('/recovery')
def show_recovery_codes():
    user = User.query.filter_by(username=session['username']).first()
    codes = user.recovery_codes.split(',')
    return render_template('recovery.html', codes=codes)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
