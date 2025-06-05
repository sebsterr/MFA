# MFA
Flask MFA (Autentificare cu Doi Factori)

Aceasta aplicatie este un sistem simplu de autentificare cu doi factori (2FA) construit cu Flask, destinat sa ofere un strat suplimentar de securitate folosind coduri TOTP (ex. Google Authenticator) si coduri de recuperare.

Caracteristici
-Inregistrare cont nou
-Autentificare clasica cu parola
-Activare autentificare TOTP (Time-based One-Time Password)
-Coduri de backup pentru recuperare
-Interfata web cu Flask + HTML + CSS

Arhitectura
-Backend: Flask, SQLAlchemy
-Baza de date: SQLite (instance/users.db)
-Securitate: Bcrypt pentru hash parole, PyOTP pentru coduri TOTP
-UI: HTML (Jinja2 templates), CSS
-QR Code: Generat automat pentru scanare in aplicatii de tip Authenticator

mfa/
├── 2FA.py                    - Aplicatia principala Flask  
├── instance/users.db         - Baza de date locala SQLite  
├── static/style.css          - Fisier CSS  
└── templates/                - Sabloane HTML  
    ├── base.html  
    ├── dashboard.html  
    ├── login.html  
    ├── recovery.html  
    ├── register.html  
    └── two_factor.html  

Instalare si Rulare
    
pip install flask flask_sqlalchemy flask_bcrypt pyotp qrcode
python 2FA.py
Aplicatia va rula la: http://localhost:5000

Resurse si Documentatie
-Flask: https://flask.palletsprojects.com/
-SQLAlchemy: https://docs.sqlalchemy.org/
-PyOTP: https://pyauth.github.io/pyotp/
-qrcode: https://pypi.org/project/qrcode/
-Google Authenticator: https://support.google.com/accounts/answer/1066447
