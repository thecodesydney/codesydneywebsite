from flask import Flask, render_template, g, request, session, redirect, url_for, jsonify, make_response, Blueprint
from flask_restplus import Api, Resource, fields
from functions import current_year
from flask_sqlalchemy import SQLAlchemy
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from forms import InputForm, LoginForm, RegisterForm, VueInputForm, ReactInputForm
from flask_cors import CORS
import sqlite3
import os, re
from os import path

app = Flask(__name__)
CORS(app)

blueprint_codesydneysiders = Blueprint('api_codesydneysiders', __name__, url_prefix='/api')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    messages = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Messages('{self.name}', '{self.email}', '{self.messages}')"

@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    submission = False
    if request.method == 'POST':
        new_message = Messages(name=request.form['name'], email=request.form['email'], messages=request.form['message'])
        db.session.add(new_message)
        db.session.commit()
        return render_template('thanks.html', messages=True)
    return render_template('index.html', year=current_year(), submission=submission)

@app.route('/jsstudygroup', methods=['GET', 'POST'])
def jsstudygroup():
    db = get_db()
    fccamperslist = []
    try: 
        cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, \
                                B1, B2, B3, B4, B5, B6, B7, B8, B9, B10,  \
                                B11, B12, B13, B14, B15, B16, B17, B18, B19, B20,  \
                                B21, B22, B23, B24, B25, B26, B27, B28, B29, B30, \
                                C1, C2, C3, C4, C5, C6, C7, C8  \
                            from vuedashboardtable \
                            order by Completed_Count desc')
    except Exception as e:
        print('Exception: ',e)    
    
    res = cur.fetchall()

    for row in res:
        statuslisttemp = []
        name  = row[0]
        for i in range(4,52):
            status = row[i]
            if status == 'Completed':
                statuslisttemp.append('▩')
            else:
                statuslisttemp.append('▥')
        statuslist = "".join(str(x) for x in statuslisttemp) 
        name_string = "".join(str(name))
        selected_fields = [name_string,statuslist]
        fccamperslist.append(selected_fields)

    return render_template('jsstudygroup.html',
                           fccamperslist=fccamperslist)


@app.route('/odinstudygroup', methods=['GET', 'POST'])
def odinstudygroup():
    db = get_db()
    fccamperslist = []
    try: 
        cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, \
                                A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, \
                                A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, \
                                A31, A32, A33, A34, A35, A36, A37, A38, A39, A40, A41, A42, A43, A44, A45 \
                            from reactdashboardtable \
                            order by Completed_Count desc')    
    except Exception as e:
        print('Exception: ',e)    
    
    res = cur.fetchall()

    for row in res:
        statuslisttemp = []
        name  = row[0]
        for i in range(4,49):
            status = row[i]
            if status == 'Completed':
                statuslisttemp.append('▩')
            else:
                statuslisttemp.append('▥')
        statuslist = "".join(str(x) for x in statuslisttemp) 
        name_string = "".join(str(name))
        selected_fields = [name_string,statuslist]
        fccamperslist.append(selected_fields)

    return render_template('odinstudygroup.html',
                           fccamperslist=fccamperslist)

@app.route('/awards', methods=['GET', 'POST'])
def awards():
    return render_template('awards.html')

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    return render_template('gallery.html')

@app.route('/volunteering', methods=['GET', 'POST'])
def volunteering():
    return render_template('volunteering.html')

@app.route('/hustlers', methods=['GET', 'POST'])
def hustlers():
    return render_template('hustlers.html')

@app.route('/fellowship', methods=['GET', 'POST'])
def fellowship():
    return render_template('fellowship.html')

@app.route('/opend', methods=['GET', 'POST'])
def opend():
    return render_template('opend.html')

@app.route('/newsletter', methods=['GET', 'POST'])
def newsletter():
    return render_template('newsletter.html')

@app.route('/merch', methods=['GET', 'POST'])
def merch():
    return render_template('merch.html')

@app.route('/support', methods=['GET', 'POST'])
def support():
    return render_template('support.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/acnc_data_profile', methods=['GET', 'POST'])
def acnc_data_profile():
    return render_template('acnc_data_profile.html')

@app.route('/messages')
def messages():
    all_messages = Messages.query.all()
    return render_template('messages.html', year=current_year(), messages=True, all_messages=all_messages)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html', messages=True)

@app.route('/fccleaderboard', methods=['GET', 'POST'])
def fccleaderboard():
    db = get_db()
    fccamperslist = []
    try: 
        cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                 A1, A2, A3, A4, A5, A6, A7, A8, \
                                 B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, \
                                 C1, C2, C3, C4, C5, C6, C7, \
                                 D1, D2, D3, \
                                 E1, E2, E3, E4, \
                                 F1, F2, F3, F4, \
                                 G1, G2, G3, G4, G5 \
                            from fccdashboardtable \
                            order by Completed_Count desc')
    except Exception as e:
        print('Exception: ',e)    
    res = cur.fetchall()

    for row in res:
        statuslisttemp = []
        name  = row[0]
        for i in range(4,45):
            status = row[i]
            if status == 'Completed':
                statuslisttemp.append('▩')
            else:
                statuslisttemp.append('▥')
        statuslist = "".join(str(x) for x in statuslisttemp) 
        name_string = "".join(str(name))
        selected_fields = [name_string,statuslist]
        fccamperslist.append(selected_fields)

    return render_template('fccleaderboard.html',
                           fccamperslist=fccamperslist)

@app.route('/fccleaderboardlogin', methods=['GET', 'POST'])
def fccleaderboardlogin():
    loginform = LoginForm() 
    error = None
    if request.method == 'POST':
        db = get_db()
        Email = loginform.LoginEmail.data       
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from fccdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    
        numRows = (len(user_cur.fetchall()))

        try: 
            user_cur = db.execute('SELECT Name, Email, Password from fccdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    

        if numRows == 1:
            res = user_cur.fetchall()
            for row in res:
                Name  = row[0]
                Email = row[1]
                Password = row[2]
                if Password == loginform.LoginPassword.data:
                    session['tempemail'] = Email
                    return redirect(url_for('fccleaderboardupdate'))         
                else:
                    error = 'The password is incorrect.'
        else:
            error = 'The username is incorrect'
        return render_template('fccleaderboardlogin.html',
                                loginform=loginform,
                                error=error)
    else:
        return render_template('fccleaderboardlogin.html',
                                loginform=loginform)

@app.route('/jsstudygrouplogin', methods=['GET', 'POST'])
def jsstudygrouplogin():
    loginform = LoginForm() 
    error = None
    if request.method == 'POST':
        db = get_db()
        Email = loginform.LoginEmail.data       
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from vuedashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    
        numRows = (len(user_cur.fetchall()))

        try: 
            user_cur = db.execute('SELECT Name, Email, Password from vuedashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    

        if numRows == 1:
            res = user_cur.fetchall()
            for row in res:
                Name  = row[0]
                Email = row[1]
                Password = row[2]
                if Password == loginform.LoginPassword.data:
                    session['tempemail'] = Email
                    return redirect(url_for('jsstudygroupupdate'))         
                else:
                    error = 'The password is incorrect.'
        else:
            error = 'The username is incorrect'
        return render_template('jsstudygrouplogin.html',
                                loginform=loginform,
                                error=error)
    else:
        return render_template('jsstudygrouplogin.html',
                                loginform=loginform)

@app.route('/odinstudygrouplogin', methods=['GET', 'POST'])
def odinstudygrouplogin():
    loginform = LoginForm() 
    error = None
    if request.method == 'POST':
        db = get_db()
        Email = loginform.LoginEmail.data       
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from reactdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    
        numRows = (len(user_cur.fetchall()))

        try: 
            user_cur = db.execute('SELECT Name, Email, Password from reactdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    

        if numRows == 1:
            res = user_cur.fetchall()
            for row in res:
                Name  = row[0]
                Email = row[1]
                Password = row[2]
                if Password == loginform.LoginPassword.data:
                    session['tempemail'] = Email
                    return redirect(url_for('odinstudygroupupdate'))         
                else:
                    error = 'The password is incorrect.'
        else:
            error = 'The username is incorrect'
        return render_template('odinstudygrouplogin.html',
                                loginform=loginform,
                                error=error)
    else:
        return render_template('odinstudygrouplogin.html',
                                loginform=loginform)


@app.route('/fccleaderboardregister', methods=['GET', 'POST'])
def fccleaderboardregister():
    registerform = RegisterForm() 
    error = None
    if request.method == 'POST':
        db = get_db()
        Email = registerform.RegisterEmail.data   
        NameList = re.findall('^[^@]+', Email)
        Name = ''.join(NameList)
        Password = registerform.RegisterPassword.data
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from fccdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    
        numRows = (len(user_cur.fetchall()))
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from fccdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        if numRows == 1:
            error='Email already exists!'
            return render_template('fccleaderboardregister.html', 
                                    registerform=registerform,
                                    error=error)
        else:
            if Email != '':
                db.execute('INSERT into fccdashboardtable \
                                (Name, Email, Password, Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, C1, C2, C3, C4, C5, C6, C7, D1, D2, D3, E1, E2, E3, E4, F1, F2, F3, F4, G1, G2, G3, G4, G5) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [Name, Email, Password, 0, 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started'])
                db.commit()                
                session['tempemail'] = Email
                return redirect(url_for('fccleaderboardupdate'))
            else:
                error='Please enter valid email'
                return render_template('fccleaderboardregister.html', 
                                        registerform=registerform,
                                        error=error)
    else:
        return render_template('fccleaderboardregister.html',
                                registerform=registerform)

@app.route('/jsstudygroupregister', methods=['GET', 'POST'])
def jsstudygroupregister():
    registerform = RegisterForm() 
    error = None
    if request.method == 'POST':
        db = get_db()
        Email = registerform.RegisterEmail.data   
        NameList = re.findall('^[^@]+', Email)
        Name = ''.join(NameList)
        Password = registerform.RegisterPassword.data
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from vuedashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    
        numRows = (len(user_cur.fetchall()))
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from vuedashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        if numRows == 1:
            error='Email already exists!'
            return render_template('jsstudygroupregister.html', 
                                    registerform=registerform,
                                    error=error)
        else:
            if Email != '':
                db.execute('INSERT into vuedashboardtable \
                                (Name, Email, Password, Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, B21, B22, B23, B24, B25, B26, B27, B28, B29, B30, C1, C2, C3, C4, C5, C6, C7, C8) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [Name, Email, Password, 0, 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started','Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started'])
                db.commit()                
                session['tempemail'] = Email
                return redirect(url_for('jsstudygroupupdate'))
            else:
                error='Please enter valid email'
                return render_template('jsstudygroupregister.html', 
                                        registerform=registerform,
                                        error=error)
    else:
        return render_template('jsstudygroupregister.html',
                                registerform=registerform)


@app.route('/odinstudygroupregister', methods=['GET', 'POST'])
def odinstudygroupregister():
    registerform = RegisterForm() 
    error = None
    if request.method == 'POST':
        db = get_db()
        Email = registerform.RegisterEmail.data   
        NameList = re.findall('^[^@]+', Email)
        Name = ''.join(NameList)
        Password = registerform.RegisterPassword.data
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from reactdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    
        numRows = (len(user_cur.fetchall()))
        try: 
            user_cur = db.execute('SELECT Name, Email, Password from reactdashboardtable where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        if numRows == 1:
            error='Email already exists!'
            return render_template('odinstudygroupregister.html', 
                                    registerform=registerform,
                                    error=error)
        else:
            if Email != '':
                db.execute('INSERT into reactdashboardtable \
                                (Name, Email, Password, Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, A31, A32, A33, A34, A35, A36, A37, A38, A39, A40, A41, A42, A43, A44, A45) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [Name, Email, Password, 0, 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started'])
                db.commit()                
                session['tempemail'] = Email
                return redirect(url_for('odinstudygroupupdate'))
            else:
                error='Please enter valid email'
                return render_template('odinstudygroupregister.html',
                                        registerform=registerform,
                                        error=error)
    else:
        return render_template('odinstudygroupregister.html',
                                registerform=registerform)


@app.route('/fccleaderboardupdate',methods=['GET','POST'])
def fccleaderboardupdate():
    form = InputForm() 

    if request.method == 'POST':
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, \
                                     B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, \
                                     C1, C2, C3, C4, C5, C6, C7, \
                                     D1, D2, D3, \
                                     E1, E2, E3, E4, \
                                     F1, F2, F3, F4, \
                                     G1, G2, G3, G4, G5 \
                                from fccdashboardtable \
                                where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        res = user_cur.fetchall()
        for row in res:
            Name  = row[0]
            Email = row[1]
            Password = row[2]
            Completed_Count = row[3]

        Completed_Count = 0    
        A1 = form.A1.data
        if A1 == 'Completed':  
            Completed_Count += 1
        A2 = form.A2.data  
        if A2 == 'Completed':  
            Completed_Count += 1
        A3 = form.A3.data  
        if A3 == 'Completed':  
            Completed_Count += 1
        A4 = form.A4.data  
        if A4 == 'Completed':  
            Completed_Count += 1
        A5 = form.A5.data
        if A5 == 'Completed':  
            Completed_Count += 1
        A6 = form.A6.data
        if A6 == 'Completed':  
            Completed_Count += 1
        A7 = form.A7.data
        if A7 == 'Completed':  
            Completed_Count += 1       
        A8 = form.A8.data
        if A8 == 'Completed':  
            Completed_Count += 1          
        B1 = form.B1.data
        if B1 == 'Completed':  
            Completed_Count += 1      
        B2 = form.B2.data
        if B2 == 'Completed':  
            Completed_Count += 1    
        B3 = form.B3.data
        if B3 == 'Completed':  
            Completed_Count += 1    
        B4 = form.B4.data
        if B4 == 'Completed':  
            Completed_Count += 1    
        B5 = form.B5.data
        if B5 == 'Completed':  
            Completed_Count += 1    
        B6 = form.B6.data
        if B6 == 'Completed':  
            Completed_Count += 1    
        B7 = form.B7.data
        if B7 == 'Completed':  
            Completed_Count += 1    
        B8 = form.B8.data
        if B8 == 'Completed':  
            Completed_Count += 1    
        B9 = form.B9.data
        if B9 == 'Completed':  
            Completed_Count += 1    
        B10 = form.B10.data
        if B10 == 'Completed':  
            Completed_Count += 1    
        C1 = form.C1.data
        if C1 == 'Completed':  
            Completed_Count += 1    
        C2 = form.C2.data
        if C2 == 'Completed':  
            Completed_Count += 1    
        C3 = form.C3.data
        if C3 == 'Completed':  
            Completed_Count += 1    
        C4 = form.C4.data
        if C4 == 'Completed':  
            Completed_Count += 1    
        C5 = form.C5.data
        if C5 == 'Completed':  
            Completed_Count += 1    
        C6 = form.C6.data
        if C6 == 'Completed':  
            Completed_Count += 1    
        C7 = form.C7.data
        if C7 == 'Completed':  
            Completed_Count += 1    
        D1 = form.D1.data
        if D1 == 'Completed':  
            Completed_Count += 1    
        D2 = form.D2.data
        if D2 == 'Completed':  
            Completed_Count += 1    
        D3 = form.D3.data
        if D3 == 'Completed':  
            Completed_Count += 1    
        E1 = form.E1.data
        if E1 == 'Completed':  
            Completed_Count += 1    
        E2 = form.E2.data
        if E2 == 'Completed':  
            Completed_Count += 1    
        E3 = form.E3.data
        if E3 == 'Completed':  
            Completed_Count += 1    
        E4 = form.E4.data
        if E4 == 'Completed':  
            Completed_Count += 1    
        F1 = form.F1.data
        if F1 == 'Completed':  
            Completed_Count += 1    
        F2 = form.F2.data
        if F2 == 'Completed':  
            Completed_Count += 1    
        F3 = form.F3.data
        if F3 == 'Completed':  
            Completed_Count += 1    
        F4 = form.F4.data
        if F4 == 'Completed':  
            Completed_Count += 1    
        G1 = form.G1.data
        if G1 == 'Completed':  
            Completed_Count += 1    
        G2 = form.G2.data
        if G2 == 'Completed':  
            Completed_Count += 1    
        G3 = form.G3.data
        if G3 == 'Completed':  
            Completed_Count += 1    
        G4 = form.G4.data
        if G4 == 'Completed':  
            Completed_Count += 1    
        G5 = form.G5.data
        if G5 == 'Completed':  
            Completed_Count += 1    
        try:
            db.execute('UPDATE fccdashboardtable \
                         SET Completed_Count=?, A1=?, A2=?, A3=?, A4=?, A5=?, A6=?, A7=?, A8=?, B1=?, B2=?, B3=?, B4=?, B5=?, B6=?, B7=?, B8=?, B9=?, B10=?, C1=?, C2=?, C3=?, C4=?, C5=?, C6=?, C7=?, D1=?, D2=?, D3=?, E1=?, E2=?, E3=?, E4=?, F1=?, F2=?, F3=?, F4=?, G1=?, G2=?, G3=?, G4=?, G5=? \
                        WHERE Email = ?', (Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, C1, C2, C3, C4, C5, C6, C7, D1, D2, D3, E1, E2, E3, E4, F1, F2, F3, F4, G1, G2, G3, G4, G5, Email))
            db.commit()
        except Exception as e:
            print(e)

        form.A1.data = A1   
        form.A2.data = A2   
        form.A3.data = A3   
        form.A4.data = A4   
        form.A5.data = A5 
        form.A6.data = A6 
        form.A7.data = A7 
        form.A8.data = A8 
        form.B1.data = B1 
        form.B2.data = B2 
        form.B3.data = B3 
        form.B4.data = B4 
        form.B5.data = B5 
        form.B6.data = B6 
        form.B7.data = B7 
        form.B8.data = B8 
        form.B9.data = B9 
        form.B10.data = B10
        form.C1.data = C1 
        form.C2.data = C2 
        form.C3.data = C3 
        form.C4.data = C4 
        form.C5.data = C5 
        form.C6.data = C6 
        form.C7.data = C7 
        form.D1.data = D1 
        form.D2.data = D2 
        form.D3.data = D3 
        form.E1.data = E1 
        form.E2.data = E2 
        form.E3.data = E3 
        form.E4.data = E4 
        form.F1.data = F1 
        form.F2.data = F2 
        form.F3.data = F3 
        form.F4.data = F4 
        form.G1.data = G1 
        form.G2.data = G2 
        form.G3.data = G3 
        form.G4.data = G4 
        form.G5.data = G5 

        return render_template('fccleaderboardupdate.html',
                                form=form)
    else:        
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, \
                                     B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, \
                                     C1, C2, C3, C4, C5, C6, C7, \
                                     D1, D2, D3, \
                                     E1, E2, E3, E4, \
                                     F1, F2, F3, F4, \
                                     G1, G2, G3, G4, G5 \
                                from fccdashboardtable \
                                where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)    

        res = user_cur.fetchall()
        for row in res:
            Name  = row[0]
            Email = row[1]
            Password = row[2]
            Completed_Count = row[3]                        
            A1 = row[4]
            A2 = row[5]
            A3 = row[6]
            A4 = row[7]
            A5 = row[8]
            A6 = row[9]
            A7 = row[10]
            A8 = row[11]
            B1 = row[12]
            B2 = row[13]
            B3 = row[14]
            B4 = row[15]
            B5 = row[16]
            B6 = row[17]
            B7 = row[18]
            B8 = row[19]
            B9 = row[20]
            B10 = row[21]
            C1 = row[22]
            C2 = row[23]
            C3 = row[24]
            C4 = row[25]
            C5 = row[26]
            C6 = row[27]
            C7 = row[28]
            D1 = row[29]
            D2 = row[30]
            D3 = row[31]
            E1 = row[32]
            E2 = row[33]
            E3 = row[34]
            E4 = row[35]
            F1 = row[36]
            F2 = row[37]
            F3 = row[38]
            F4 = row[39]
            G1 = row[40]
            G2 = row[41]
            G3 = row[42]
            G4 = row[43]
            G5 = row[44]

        form.Email.data = Email
        form.Password.data = Password 
        form.A1.data = A1  
        form.A2.data = A2  
        form.A3.data = A3  
        form.A4.data = A4  
        form.A5.data = A5
        form.A6.data = A6
        form.A7.data = A7
        form.A8.data = A8
        form.B1.data = B1
        form.B2.data = B2
        form.B3.data = B3
        form.B4.data = B4
        form.B5.data = B5
        form.B6.data = B6
        form.B7.data = B7
        form.B8.data = B8
        form.B9.data = B9
        form.B10.data = B10
        form.C1.data = C1
        form.C2.data = C2
        form.C3.data = C3
        form.C4.data = C4
        form.C5.data = C5
        form.C6.data = C6
        form.C7.data = C7
        form.D1.data = D1
        form.D2.data = D2
        form.D3.data = D3
        form.E1.data = E1
        form.E2.data = E2
        form.E3.data = E3
        form.E4.data = E4
        form.F1.data = F1
        form.F2.data = F2
        form.F3.data = F3
        form.F4.data = F4
        form.G1.data = G1
        form.G2.data = G2
        form.G3.data = G3
        form.G4.data = G4
        form.G5.data = G5
        return render_template('fccleaderboardupdate.html',
                                form=form,
                                Name=Name)


@app.route('/jsstudygroupupdate',methods=['GET','POST'])
def jsstudygroupupdate():
    form = VueInputForm() 

    if request.method == 'POST':
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, \
                                     B1, B2, B3, B4, B5, B6, B7, B8, B9, B10,  \
                                     B11, B12, B13, B14, B15, B16, B17, B18, B19, B20,  \
                                     B21, B22, B23, B24, B25, B26, B27, B28, B29, B30,  \
                                     C1, C2, C3, C4, C5, C6, C7, C8 \
                                from vuedashboardtable \
                                where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        res = user_cur.fetchall()
        for row in res:
            Name  = row[0]
            Email = row[1]
            Password = row[2]
            Completed_Count = row[3]

        Completed_Count = 0    
        A1 = form.A1.data
        if A1 == 'Completed':  
            Completed_Count += 1
        A2 = form.A2.data  
        if A2 == 'Completed':  
            Completed_Count += 1
        A3 = form.A3.data  
        if A3 == 'Completed':  
            Completed_Count += 1
        A4 = form.A4.data  
        if A4 == 'Completed':  
            Completed_Count += 1
        A5 = form.A5.data
        if A5 == 'Completed':  
            Completed_Count += 1
        A6 = form.A6.data
        if A6 == 'Completed':  
            Completed_Count += 1
        A7 = form.A7.data
        if A7 == 'Completed':  
            Completed_Count += 1       
        A8 = form.A8.data
        if A8 == 'Completed':  
            Completed_Count += 1          
        A9 = form.A9.data
        if A9 == 'Completed':  
            Completed_Count += 1      
        A10 = form.A10.data
        if A10 == 'Completed':  
            Completed_Count += 1 
        B1 = form.B1.data
        if B1 == 'Completed':  
            Completed_Count += 1 
        B2 = form.B2.data
        if B2 == 'Completed':  
            Completed_Count += 1 
        B3 = form.B3.data
        if B3 == 'Completed':  
            Completed_Count += 1 
        B4 = form.B4.data
        if B4 == 'Completed':  
            Completed_Count += 1 
        B5 = form.B5.data
        if B5 == 'Completed':  
            Completed_Count += 1 
        B6 = form.B6.data
        if B6 == 'Completed':  
            Completed_Count += 1 
        B7 = form.B7.data
        if B7 == 'Completed':  
            Completed_Count += 1 
        B8 = form.B8.data
        if B8 == 'Completed':  
            Completed_Count += 1 
        B9 = form.B9.data
        if B9 == 'Completed':  
            Completed_Count += 1 
        B10 = form.B10.data
        if B10 == 'Completed':  
            Completed_Count += 1 
        B11 = form.B11.data
        if B11 == 'Completed':  
            Completed_Count += 1 
        B12 = form.B12.data
        if B12 == 'Completed':  
            Completed_Count += 1 
        B13 = form.B13.data
        if B13 == 'Completed':  
            Completed_Count += 1 
        B14 = form.B14.data
        if B14 == 'Completed':  
            Completed_Count += 1 
        B15 = form.B15.data
        if B15 == 'Completed':  
            Completed_Count += 1 
        B16 = form.B16.data
        if B16 == 'Completed':  
            Completed_Count += 1 
        B17 = form.B17.data
        if B17 == 'Completed':  
            Completed_Count += 1 
        B18 = form.B18.data
        if B18 == 'Completed':  
            Completed_Count += 1 
        B19 = form.B19.data
        if B19 == 'Completed':  
            Completed_Count += 1 
        B20 = form.B20.data
        if B20 == 'Completed':  
            Completed_Count += 1 
        B21 = form.B21.data
        if B21 == 'Completed':  
            Completed_Count += 1 
        B22 = form.B22.data
        if B22 == 'Completed':  
            Completed_Count += 1 
        B23 = form.B23.data
        if B23 == 'Completed':  
            Completed_Count += 1 
        B24 = form.B24.data
        if B24 == 'Completed':  
            Completed_Count += 1 
        B25 = form.B25.data
        if B25 == 'Completed':  
            Completed_Count += 1 
        B26 = form.B26.data
        if B26 == 'Completed':  
            Completed_Count += 1 
        B27 = form.B27.data
        if B27 == 'Completed':  
            Completed_Count += 1 
        B28 = form.B28.data
        if B28 == 'Completed':  
            Completed_Count += 1 
        B29 = form.B29.data
        if B29 == 'Completed':  
            Completed_Count += 1 
        B30 = form.B30.data
        if B30 == 'Completed':  
            Completed_Count += 1 
        C1 = form.C1.data
        if C1 == 'Completed':  
            Completed_Count += 1
        C2 = form.C2.data
        if C2 == 'Completed':  
            Completed_Count += 1
        C3 = form.C3.data
        if C3 == 'Completed':  
            Completed_Count += 1
        C4 = form.C4.data
        if C4 == 'Completed':  
            Completed_Count += 1
        C5 = form.C5.data
        if C5 == 'Completed':  
            Completed_Count += 1
        C6 = form.C6.data
        if C6 == 'Completed':  
            Completed_Count += 1
        C7 = form.C7.data
        if C7 == 'Completed':  
            Completed_Count += 1
        C8 = form.C8.data
        if C8 == 'Completed':  
            Completed_Count += 1
        try:
            db.execute('UPDATE vuedashboardtable \
                         SET Completed_Count=?, A1=?, A2=?, A3=?, A4=?, A5=?, A6=?, A7=?, A8=?, A9=?, A10=?, B1=?, B2=?, B3=?, B4=?, B5=?, B6=?, B7=?, B8=?, B9=?, B10=?, B11=?, B12=?, B13=?, B14=?, B15=?, B16=?, B17=?, B18=?, B19=?, B20=?, B21=?, B22=?, B23=?, B24=?, B25=?, B26=?, B27=?, B28=?, B29=?, B30=?, C1=?, C2=?, C3=?, C4=?, C5=?, C6=?, C7=?, C8=? \
                        WHERE Email = ?', (Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, B21, B22, B23, B24, B25, B26, B27, B28, B29, B30, C1, C2, C3, C4, C5, C6, C7, C8, Email))                        
            db.commit()
        except Exception as e:
            print(e)

        form.A1.data = A1   
        form.A2.data = A2   
        form.A3.data = A3   
        form.A4.data = A4   
        form.A5.data = A5 
        form.A6.data = A6 
        form.A7.data = A7 
        form.A8.data = A8 
        form.A9.data = A9 
        form.A10.data = A10 
        form.B1.data = B1   
        form.B2.data = B2   
        form.B3.data = B3   
        form.B4.data = B4   
        form.B5.data = B5 
        form.B6.data = B6 
        form.B7.data = B7 
        form.B8.data = B8 
        form.B9.data = B9 
        form.B10.data = B10 
        form.B11.data = B11  
        form.B12.data = B12   
        form.B13.data = B13   
        form.B14.data = B14   
        form.B15.data = B15 
        form.B16.data = B16 
        form.B17.data = B17 
        form.B18.data = B18 
        form.B19.data = B19 
        form.B20.data = B20 
        form.B21.data = B21  
        form.B22.data = B22   
        form.B23.data = B23   
        form.B24.data = B24   
        form.B25.data = B25 
        form.B26.data = B26 
        form.B27.data = B27 
        form.B28.data = B28 
        form.B29.data = B29 
        form.B30.data = B30 
        form.C1.data = C1
        form.C2.data = C2
        form.C3.data = C3
        form.C4.data = C4
        form.C5.data = C5
        form.C6.data = C6
        form.C7.data = C7
        form.C8.data = C8
        
        return render_template('jsstudygroupupdate.html',
                                form=form)
    else:        
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, \
                                     B1, B2, B3, B4, B5, B6, B7, B8, B9, B10,  \
                                     B11, B12, B13, B14, B15, B16, B17, B18, B19, B20,  \
                                     B21, B22, B23, B24, B25, B26, B27, B28, B29, B30,  \
                                     C1, C2, C3, C4, C5, C6, C7, C8 \
                                from vuedashboardtable \
                                where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        res = user_cur.fetchall()

        for row in res:
            Name  = row[0]
            Email = row[1]
            Password = row[2]
            Completed_Count = row[3]                        
            A1 = row[4]
            A2 = row[5]
            A3 = row[6]
            A4 = row[7]
            A5 = row[8]
            A6 = row[9]
            A7 = row[10]
            A8 = row[11]
            A9 = row[12]
            A10 = row[13]
            B1 = row[14]
            B2 = row[15]
            B3 = row[16]
            B4 = row[17]
            B5 = row[18]
            B6 = row[19]
            B7 = row[20]
            B8 = row[21]
            B9 = row[22]
            B10 = row[23]
            B11 = row[24]
            B12 = row[25]
            B13 = row[26]
            B14 = row[27]
            B15 = row[28]
            B16 = row[29]
            B17 = row[30]
            B18 = row[31]
            B19 = row[32]
            B20 = row[33]
            B21 = row[34]
            B22 = row[35]
            B23 = row[36]
            B24 = row[37]
            B25 = row[38]
            B26 = row[39]
            B27 = row[40]
            B28 = row[41]
            B29 = row[42]
            B30 = row[43]
            C1 = row[44]
            C2 = row[45]
            C3 = row[46]
            C4 = row[47]
            C5 = row[48]
            C6 = row[49]
            C7 = row[50]
            C8 = row[51]

        form.Email.data = Email
        form.Password.data = Password 
        form.A1.data = A1  
        form.A2.data = A2  
        form.A3.data = A3  
        form.A4.data = A4  
        form.A5.data = A5
        form.A6.data = A6
        form.A7.data = A7
        form.A8.data = A8
        form.A9.data = A9
        form.A10.data = A10
        form.B1.data = B1  
        form.B2.data = B2  
        form.B3.data = B3  
        form.B4.data = B4  
        form.B5.data = B5
        form.B6.data = B6
        form.B7.data = B7
        form.B8.data = B8
        form.B9.data = B9
        form.B10.data = B10
        form.B11.data = B11  
        form.B12.data = B12  
        form.B13.data = B13  
        form.B14.data = B14  
        form.B15.data = B15
        form.B16.data = B16
        form.B17.data = B17
        form.B18.data = B18
        form.B19.data = B19
        form.B20.data = B20
        form.B21.data = B21  
        form.B22.data = B22  
        form.B23.data = B23  
        form.B24.data = B24  
        form.B25.data = B25
        form.B26.data = B26
        form.B27.data = B27
        form.B28.data = B28
        form.B29.data = B29
        form.B30.data = B30
        form.C1.data = C1
        form.C2.data = C2
        form.C3.data = C3
        form.C4.data = C4
        form.C5.data = C5
        form.C6.data = C6
        form.C7.data = C7
        form.C8.data = C8       

        return render_template('jsstudygroupupdate.html',
                                form=form,
                                Email=Email)

@app.route('/odinstudygroupupdate',methods=['GET','POST'])
def odinstudygroupupdate():
    form = ReactInputForm() 
    if request.method == 'POST':
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, \
                                     A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, \
                                     A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, \
                                     A31, A32, A33, A34, A35, A36, A37, A38, A39, A40, A41, A42, A43, A44, A45 \
                                from reactdashboardtable \
                                where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        res = user_cur.fetchall()
        for row in res:
            Name  = row[0]
            Email = row[1]
            Password = row[2]
            Completed_Count = row[3]

        Completed_Count = 0    
        A1 = form.A1.data
        if A1 == 'Completed':  
            Completed_Count += 1
        A2 = form.A2.data  
        if A2 == 'Completed':  
            Completed_Count += 1
        A3 = form.A3.data  
        if A3 == 'Completed':  
            Completed_Count += 1
        A4 = form.A4.data  
        if A4 == 'Completed':  
            Completed_Count += 1
        A5 = form.A5.data
        if A5 == 'Completed':  
            Completed_Count += 1
        A6 = form.A6.data
        if A6 == 'Completed':  
            Completed_Count += 1
        A7 = form.A7.data
        if A7 == 'Completed':  
            Completed_Count += 1       
        A8 = form.A8.data
        if A8 == 'Completed':  
            Completed_Count += 1          
        A9 = form.A9.data
        if A9 == 'Completed':  
            Completed_Count += 1      
        A10 = form.A10.data
        if A10 == 'Completed':  
            Completed_Count += 1 
        A11 = form.A11.data
        if A11 == 'Completed':  
            Completed_Count += 1
        A12 = form.A12.data  
        if A12 == 'Completed':  
            Completed_Count += 1
        A13 = form.A13.data  
        if A13 == 'Completed':  
            Completed_Count += 1
        A14 = form.A14.data  
        if A14 == 'Completed':  
            Completed_Count += 1
        A15 = form.A15.data
        if A15 == 'Completed':  
            Completed_Count += 1
        A16 = form.A16.data
        if A16 == 'Completed':  
            Completed_Count += 1
        A17 = form.A17.data
        if A17 == 'Completed':  
            Completed_Count += 1       
        A18 = form.A18.data
        if A18 == 'Completed':  
            Completed_Count += 1          
        A19 = form.A19.data
        if A19 == 'Completed':  
            Completed_Count += 1      
        A20 = form.A20.data
        if A20 == 'Completed':  
            Completed_Count += 1 
        A21 = form.A21.data
        if A21 == 'Completed':  
            Completed_Count += 1
        A22 = form.A22.data  
        if A22 == 'Completed':  
            Completed_Count += 1
        A23 = form.A23.data  
        if A23 == 'Completed':  
            Completed_Count += 1
        A24 = form.A24.data  
        if A24 == 'Completed':  
            Completed_Count += 1
        A25 = form.A25.data
        if A25 == 'Completed':  
            Completed_Count += 1
        A26 = form.A26.data
        if A26 == 'Completed':  
            Completed_Count += 1
        A27 = form.A27.data
        if A27 == 'Completed':  
            Completed_Count += 1       
        A28 = form.A28.data
        if A28 == 'Completed':  
            Completed_Count += 1          
        A29 = form.A29.data
        if A29 == 'Completed':  
            Completed_Count += 1      
        A30 = form.A30.data
        if A30 == 'Completed':  
            Completed_Count += 1 
        A31 = form.A31.data
        if A31 == 'Completed':  
            Completed_Count += 1
        A32 = form.A32.data  
        if A32 == 'Completed':  
            Completed_Count += 1
        A33 = form.A33.data  
        if A33 == 'Completed':  
            Completed_Count += 1
        A34 = form.A34.data  
        if A34 == 'Completed':  
            Completed_Count += 1
        A35 = form.A35.data
        if A35 == 'Completed':  
            Completed_Count += 1
        A36 = form.A36.data
        if A36 == 'Completed':  
            Completed_Count += 1
        A37 = form.A37.data
        if A37 == 'Completed':  
            Completed_Count += 1       
        A38 = form.A38.data
        if A38 == 'Completed':  
            Completed_Count += 1          
        A39 = form.A39.data
        if A39 == 'Completed':  
            Completed_Count += 1      
        A40 = form.A40.data
        if A40 == 'Completed':  
            Completed_Count += 1  
        A41 = form.A41.data
        if A41 == 'Completed':  
            Completed_Count += 1  
        A42 = form.A42.data
        if A42 == 'Completed':  
            Completed_Count += 1  
        A43 = form.A43.data
        if A43 == 'Completed':  
            Completed_Count += 1  
        A44 = form.A44.data
        if A44 == 'Completed':  
            Completed_Count += 1  
        A45 = form.A45.data
        if A45 == 'Completed':  
            Completed_Count += 1  
        try:
            db.execute('UPDATE reactdashboardtable \
                         SET Completed_Count=?, A1=?, A2=?, A3=?, A4=?, A5=?, A6=?, A7=?, A8=?, A9=?, A10=?, A11=?, A12=?, A13=?, A14=?, A15=?, A16=?, A17=?, A18=?, A19=?, A20=?, A21=?, A22=?, A23=?, A24=?, A25=?, A26=?, A27=?, A28=?, A29=?, A30=?, A31=?, A32=?, A33=?, A34=?, A35=?, A36=?, A37=?, A38=?, A39=?, A40=?, A41=?, A42=?, A43=?, A44=?, A45=? \
                        WHERE Email = ?', (Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, A31, A32, A33, A34, A35, A36, A37, A38, A39, A40, A41, A42, A43, A44, A45, Email))                        
            db.commit()
        except Exception as e:
            print(e)

        form.A1.data = A1   
        form.A2.data = A2   
        form.A3.data = A3   
        form.A4.data = A4   
        form.A5.data = A5 
        form.A6.data = A6 
        form.A7.data = A7 
        form.A8.data = A8 
        form.A9.data = A9 
        form.A10.data = A10 
        form.A11.data = A21   
        form.A12.data = A22   
        form.A13.data = A23   
        form.A14.data = A24   
        form.A15.data = A25 
        form.A16.data = A26 
        form.A17.data = A27 
        form.A18.data = A28 
        form.A19.data = A29 
        form.A20.data = A20 
        form.A21.data = A21   
        form.A22.data = A22   
        form.A23.data = A23   
        form.A24.data = A24   
        form.A25.data = A25 
        form.A26.data = A26 
        form.A27.data = A27 
        form.A28.data = A28 
        form.A29.data = A29 
        form.A30.data = A30 
        form.A31.data = A31   
        form.A32.data = A32   
        form.A33.data = A33   
        form.A34.data = A34   
        form.A35.data = A35 
        form.A36.data = A36 
        form.A37.data = A37 
        form.A38.data = A38 
        form.A39.data = A39 
        form.A40.data = A40 
        form.A41.data = A41 
        form.A42.data = A42 
        form.A43.data = A43 
        form.A44.data = A44 
        form.A45.data = A45 
                        
        return render_template('odinstudygroupupdate.html',
                                form=form)
    else:        
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, \
                                     A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, \
                                     A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, \
                                     A31, A32, A33, A34, A35, A36, A37, A38, A39, A40, A41, A42, A43, A44, A45 \
                                from reactdashboardtable \
                                where Email = ?', [Email])
        except Exception as e:
            print('Exception: ',e)

        res = user_cur.fetchall()

        for row in res:
            Name  = row[0]
            Email = row[1]
            Password = row[2]
            Completed_Count = row[3]                        
            A1 = row[4]
            A2 = row[5]
            A3 = row[6]
            A4 = row[7]
            A5 = row[8]
            A6 = row[9]
            A7 = row[10]
            A8 = row[11]
            A9 = row[12]
            A10 = row[13]
            A11 = row[14]
            A12 = row[15]
            A13 = row[16]
            A14 = row[17]
            A15 = row[18]
            A16 = row[19]
            A17 = row[20]
            A18 = row[21]
            A19 = row[22]
            A20 = row[23]
            A21 = row[24]
            A22 = row[25]
            A23 = row[26]
            A24 = row[27]
            A25 = row[28]
            A26 = row[29]
            A27 = row[30]
            A28 = row[31]
            A29 = row[32]
            A30 = row[33]
            A31 = row[34]
            A32 = row[35]
            A33 = row[36]
            A34 = row[37]
            A35 = row[38]
            A36 = row[39]
            A37 = row[40]
            A38 = row[41]
            A39 = row[42]
            A40 = row[43]
            A41 = row[44]
            A42 = row[45]
            A43 = row[46]
            A44 = row[47]
            A45 = row[48]
            
        form.Email.data = Email
        print('password',row[2])
        form.Password.data = Password       
        form.A1.data = A1
        form.A2.data = A2
        form.A3.data = A3
        form.A4.data = A4
        form.A5.data = A5
        form.A6.data = A6
        form.A7.data = A7
        form.A8.data = A8
        form.A9.data = A9
        form.A10.data = A10
        form.A11.data = A11
        form.A12.data = A12
        form.A13.data = A13
        form.A14.data = A14
        form.A15.data = A15
        form.A16.data = A16
        form.A17.data = A17
        form.A18.data = A18
        form.A19.data = A19
        form.A20.data = A20
        form.A21.data = A21
        form.A22.data = A22
        form.A23.data = A23
        form.A24.data = A24
        form.A25.data = A25
        form.A26.data = A26
        form.A27.data = A27
        form.A28.data = A28
        form.A29.data = A29
        form.A30.data = A30
        form.A31.data = A31
        form.A32.data = A32
        form.A33.data = A33
        form.A34.data = A34
        form.A35.data = A35
        form.A36.data = A36
        form.A37.data = A37
        form.A38.data = A38
        form.A39.data = A39
        form.A40.data = A40
        form.A41.data = A41
        form.A42.data = A42
        form.A43.data = A43
        form.A44.data = A44
        form.A45.data = A45

        return render_template('odinstudygroupupdate.html',
                                form=form,
                                Email=Email)

########################################################################################################################
# CodeSydneySiders API
########################################################################################################################
api = Api(blueprint_codesydneysiders, doc='/documentation', version='1.0', title='Data Service for Code.Sydney members',
          description='This is a Flask-RESTPlus data service that allows a client to consume APIs to retrieve Code.Sydney members.',
          )
app.register_blueprint(blueprint_codesydneysiders)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_codesydneysiders():
    sql = sqlite3.connect(path.join(ROOT, "codesydneysiders.db"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_codesydneysiders():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_codesydneysiders()
    return g.sqlite_db

@api.route('/codesydneysiders/all')
class AllCodeSydneySiders(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all CodeSydneysiders.')
    def get(self):
        db = get_db_codesydneysiders()
        details_cur = db.execute('select id, photo, name, title, socialURL, headline from codesydneysiders')
        details = details_cur.fetchall()

        return_values = []
        for detail in details:
            detail_dict = {}
            detail_dict['id'] = detail['id']
            detail_dict['photo'] = detail['photo']
            detail_dict['name'] = detail['name']
            detail_dict['title'] = detail['title']
            detail_dict['socialURL'] = detail['socialURL']
            detail_dict['headline'] = detail['headline']

            return_badge_values = []
            details_cur2 = db.execute('select id, codesydneysider_id, badge_order, badge_name, badge_image_name, badge from badges where codesydneysider_id = ? order by codesydneysider_id', [detail_dict['id']])
            details2 = details_cur2.fetchall()
            for detail2 in details2:
                detail2_dict = {}
                detail2_dict['badge_order'] = detail2['badge_order']
                detail2_dict['badge_name'] = detail2['badge_name']
                detail2_dict['badge_image_name'] = detail2['badge_image_name']
                detail2_dict['badge'] = detail2['badge']
                return_badge_values.append(detail2_dict)

            detail_dict['badges'] = return_badge_values
            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

if __name__ == '__main__':
    app.run(debug=True)