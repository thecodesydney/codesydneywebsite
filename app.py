from flask import Flask, render_template, g, request, session, redirect, url_for, jsonify, make_response, Blueprint
from flask_restplus import Api, Resource, fields
from functions import current_year
from flask_sqlalchemy import SQLAlchemy
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from forms import InputForm, LoginForm, RegisterForm, VueInputForm
import sqlite3
import os, re
from os import path

app = Flask(__name__)

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

'''
@app.route('/microbootcamp', methods=['GET', 'POST'])
def microbootcamp():
    return render_template('microbootcamp.html')
'''

@app.route('/vue', methods=['GET', 'POST'])
def microbootcamp():
    db = get_db()
    fccamperslist = []
    try: 
        cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                 A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, \
                                 B1, B2, B3, B4, B5, B6, B7, B8, B9 \
                            from vuedashboardtable \
                            order by Completed_Count desc')
    except Exception as e:
        print('Exception: ',e)    
    res = cur.fetchall()

    for row in res:
        statuslisttemp = []
        name  = row[0]
        for i in range(4,24):
            status = row[i]
            if status == 'Completed':
                statuslisttemp.append('▩')
            else:
                statuslisttemp.append('▥')
        statuslist = "".join(str(x) for x in statuslisttemp) 
        name_string = "".join(str(name))
        selected_fields = [name_string,statuslist]
        fccamperslist.append(selected_fields)

    return render_template('vue.html',
                           fccamperslist=fccamperslist)

@app.route('/awards', methods=['GET', 'POST'])
def awards():
    return render_template('awards.html')

@app.route('/testimonials', methods=['GET', 'POST'])
def testimonials():
    return render_template('testimonials.html')

@app.route('/fellowship', methods=['GET', 'POST'])
def fellowship():
    return render_template('fellowship.html')

@app.route('/opend', methods=['GET', 'POST'])
def opend():
    return render_template('opend.html')

@app.route('/newsletter', methods=['GET', 'POST'])
def newsletter():
    return render_template('newsletter.html')

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

@app.route('/vueleaderboardlogin', methods=['GET', 'POST'])
def vueleaderboardlogin():
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
                    return redirect(url_for('vueleaderboardupdate'))         
                else:
                    error = 'The password is incorrect.'
        else:
            error = 'The username is incorrect'
        return render_template('vueleaderboardlogin.html',
                                loginform=loginform,
                                error=error)
    else:
        return render_template('vueleaderboardlogin.html',
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

@app.route('/vueleaderboardregister', methods=['GET', 'POST'])
def vueleaderboardregister():
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
            return render_template('vueleaderboardregister.html', 
                                    registerform=registerform,
                                    error=error)
        else:
            if Email != '':
                db.execute('INSERT into vuedashboardtable \
                                (Name, Email, Password, Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, B1, B2, B3, B4, B5, B6, B7, B8, B9) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [Name, Email, Password, 0, 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started', 'Not yet started'])
                db.commit()                
                session['tempemail'] = Email
                return redirect(url_for('vueleaderboardupdate'))
            else:
                error='Please enter valid email'
                return render_template('vueleaderboardregister.html', 
                                        registerform=registerform,
                                        error=error)
    else:
        return render_template('vueleaderboardregister.html',
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


@app.route('/vueleaderboardupdate',methods=['GET','POST'])
def vueleaderboardupdate():
    form = VueInputForm() 

    if request.method == 'POST':
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, \
                                     B1, B2, B3, B4, B5, B6, B7, B8, B9 \
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
        A11 = form.A11.data
        if A11 == 'Completed':  
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
        try:
            db.execute('UPDATE vuedashboardtable \
                         SET Completed_Count=?, A1=?, A2=?, A3=?, A4=?, A5=?, A6=?, A7=?, A8=?, A9=?, A10=?, A11=?, B1=?, B2=?, B3=?, B4=?, B5=?, B6=?, B7=?, B8=?, B9=? \
                        WHERE Email = ?', (Completed_Count, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, B1, B2, B3, B4, B5, B6, B7, B8, B9, Email))
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
        form.A11.data = A11 
        form.B1.data = B1   
        form.B2.data = B2   
        form.B3.data = B3   
        form.B4.data = B4   
        form.B5.data = B5 
        form.B6.data = B6 
        form.B7.data = B7 
        form.B8.data = B8 
        form.B9.data = B9 

        return render_template('vueleaderboardupdate.html',
                                form=form)
    else:        
        db = get_db()
        Email = session.get('tempemail', None)
        try: 
            user_cur = db.execute('SELECT Name, Email, Password, Completed_Count, \
                                     A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, \
                                     B1, B2, B3, B4, B5, B6, B7, B8, B9 \
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
            A11 = row[14]
            B1 = row[15]
            B2 = row[16]
            B3 = row[17]
            B4 = row[18]
            B5 = row[19]
            B6 = row[20]
            B7 = row[21]
            B8 = row[22]
            B9 = row[23]
        
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
        form.A11.data = A11
        form.B1.data = B1  
        form.B2.data = B2  
        form.B3.data = B3  
        form.B4.data = B4  
        form.B5.data = B5
        form.B6.data = B6
        form.B7.data = B7
        form.B8.data = B8
        form.B9.data = B9

        return render_template('vueleaderboardupdate.html',
                                form=form,
                                Email=Email)

if __name__ == '__main__':
    app.run(debug=True)