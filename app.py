from flask import Flask, render_template, g, request, session, redirect, url_for, jsonify, make_response, Blueprint
from flask_restplus import Api, Resource, fields
from functions import current_year
from flask_sqlalchemy import SQLAlchemy
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from forms import InputForm, LoginForm, RegisterForm
import sqlite3
import os, re
from os import path

app = Flask(__name__)
blueprint_topbaby = Blueprint('api_topbaby', __name__, url_prefix='/api_topbaby')
blueprint_topbabynames = Blueprint('api_topbabynames', __name__, url_prefix='/api_topbabynames')
blueprint_opaltrain = Blueprint('api_opaltrain', __name__, url_prefix='/api_opaltrain')
blueprint_opaltraincardtype = Blueprint('api_opaltraincardtype', __name__, url_prefix='/api_opaltraincardtype')
blueprint_contingentworkforce = Blueprint('api_contingentworkforce', __name__, url_prefix='/api_contingentworkforce')
blueprint_acnc = Blueprint('api_acnc', __name__, url_prefix='/api_acnc')

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


########################################################################################################################
# NSW birth rate API
########################################################################################################################
api = Api(blueprint_topbaby, doc='/documentation', version='1.0', title='Data Service for NSW birth rate information by suburb',
          description='This is a Flask-RESTPlus data service that allows a client to consume APIs related to NSW birth rate information by suburb.',
          )
app.register_blueprint(blueprint_topbaby)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_topbaby():
    sql = sqlite3.connect(path.join(ROOT, "NSW_BIRTH_RATE.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_topbaby():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_topbaby()
    return g.sqlite_db

@api.route('/topbaby/all')
class TopBabyAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all suburbs.')
    def get(self):
        db = get_db_topbaby()
        details_cur = db.execute('select YEAR, LOCALITY, SUBURB, STATE, POSTCODE, COUNT from NSW_BIRTH_RATE')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['LOCALITY'] = detail['LOCALITY']
            detail_dict['SUBURB'] = detail['SUBURB']
            detail_dict['STATE'] = detail['STATE']
            detail_dict['POSTCODE'] = detail['POSTCODE']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/topbaby/<string:SUBURB>', methods=['GET'])
class TopBabySuburb(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for one suburb.')
    def get(self, SUBURB):
        db = get_db_topbaby()
        details_cur = db.execute(
            'select YEAR, LOCALITY, SUBURB, STATE, POSTCODE, COUNT from NSW_BIRTH_RATE where SUBURB = ? COLLATE NOCASE', [SUBURB])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['LOCALITY'] = detail['LOCALITY']
            detail_dict['SUBURB'] = detail['SUBURB']
            detail_dict['STATE'] = detail['STATE']
            detail_dict['POSTCODE'] = detail['POSTCODE']
            detail_dict['COUNT'] = detail['COUNT']\

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Top baby names from 2010 to 2018 API
########################################################################################################################
api = Api(blueprint_topbabynames, doc='/documentation', version='1.0', title='Data Service for top 100 Popular Baby Names from 2010 to 2018 in NSW',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to top 100 popular baby names from 2010 and 2018 in NSW.',
          )

app.register_blueprint(blueprint_topbabynames)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_topbabynames():
    sql = sqlite3.connect(path.join(ROOT, "PopularBabyName.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_topbabynames():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_topbabynames()
    return g.sqlite_db

@api.route('/topbabynames/all')
class TopBabyNamesAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all.')
    def get(self):
        db = get_db_topbabynames()
        details_cur = db.execute('select NAME, GENDER, YEAR, NUMBER from PopularBN')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['NAME'] = detail['NAME']
            detail_dict['GENDER'] = detail['GENDER']
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['NUMBER'] = detail['NUMBER']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/topbabynames/all/<string:YEAR>/<string:GENDER>', methods=['GET'])
class TopBabyNamesYearGender(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for specific year and sex.')
    @api.doc(params={'GENDER': 'fill in boys/girls, case-insensitive','YEAR':'e.g. 2018'})
    def get(self, YEAR, GENDER):
        db = get_db_topbabynames()
        details_cur = db.execute(
            'select NAME, GENDER, YEAR, NUMBER from PopularBN where YEAR = ? COLLATE NOCASE and GENDER = ? COLLATE NOCASE', [YEAR, GENDER])
        details = details_cur.fetchall()
        return_values = []
        for detail in details:
            detail_dict = {}
            detail_dict['NAME'] = detail['NAME']
            detail_dict['GENDER'] = detail['GENDER']
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['NUMBER'] = detail['NUMBER']\

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Train Opal Trips (July 2016 to April 2019) API
########################################################################################################################
api = Api(blueprint_opaltrain, version='1.0', doc='/documentation', title='Data Service for NSW train line monthly Opal trips covering July 2016 to April 2019.',
          description='This is a Flask-RESTPlus data service that allows a client to consume APIs related to NSW train line monthly Opal trips from July 2016 to April 2019.',
          )

app.register_blueprint(blueprint_opaltrain)

# Database helper
def connect_db_opaltrain():
    sql = sqlite3.connect(path.join(ROOT, "NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_opaltrain():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_opaltrain()
    return g.sqlite_db

@api.route('/opaltrain/all')
class NSWOpalAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all train lines.')
    def get(self):
        db = get_db_opaltrain()
        details_cur = db.execute('select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/opaltrain/all/period/<string:PERIOD>', methods=['GET'])
class NSWOpalPeriod(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected period.')
    def get(self, PERIOD):
        db = get_db_opaltrain()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019 where PERIOD = ? COLLATE NOCASE',
            [PERIOD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/opaltrain/all/trainline/<string:TRAIN_LINE>', methods=['GET'])
class NSWOpalTrainLine(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for selected train line.')
    def get(self, TRAIN_LINE):
        db = get_db_opaltrain()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019 where TRAIN_LINE like ? COLLATE NOCASE',
            ["%" + TRAIN_LINE + "%"])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/opaltrain/all/TRAIN_LINE/PERIOD/<string:TRAIN_LINE>/<string:PERIOD>', methods=['GET'])
class NSWOpalTrainLinePeriod(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for selected train line and period.')
    def get(self, TRAIN_LINE, PERIOD):
        db = get_db_opaltrain()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019 where (TRAIN_LINE like ? COLLATE NOCASE and PERIOD = ? COLLATE NOCASE)',
            ["%" + TRAIN_LINE + "%", PERIOD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Train Opal Card Type Monthly Figures (July 2016 to April 2019) API
########################################################################################################################
api = Api(blueprint_opaltraincardtype, version='1.0', doc='/documentation', title='Data Service for NSW opal card type monthly figures. July 2016 to April 2019.',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to NSW opal card type monthly figures. July 2016 to April 2019.',
          )

app.register_blueprint(blueprint_opaltraincardtype)

# Database helper
def connect_db_opaltraincardtype():
    sql = sqlite3.connect(path.join(ROOT, "NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_opaltraincardtype():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_opaltraincardtype()
    return g.sqlite_db

@api.route('/opaltraincardtype/all')
class NSWOpalAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all train lines.')
    def get(self):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/TRAIN_LINE/<string:TRAIN_LINE>', methods=['GET'])
class NSWOpalTrainLine(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for selected train line.')
    def get(self, TRAIN_LINE):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where TRAIN_LINE like ? COLLATE NOCASE',
            ["%" + TRAIN_LINE + "%"])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/CARD_TYPE/<string:CARD_TYPE>', methods=['GET'])
class NSWOpalCardType(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected CARD_TYPE.')
    def get(self, CARD_TYPE):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where CARD_TYPE = ? COLLATE NOCASE',
            [CARD_TYPE])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/PERIOD/<string:PERIOD>', methods=['GET'])
class NSWOpalPeriod(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected PERIOD.')
    def get(self, PERIOD):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where PERIOD = ? COLLATE NOCASE',
            [PERIOD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/TRAIN_LINE/PERIOD_or_CARD/<string:TRAIN_LINE>/<string:PERIOD_or_CARD>', methods=['GET'])
class NSWOpalTrainLinePeriodCardType(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected TRAIN LINE and PERIOD or CARD.')
    def get(self, TRAIN_LINE, PERIOD_or_CARD):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, CARD_TYPE, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where (TRAIN_LINE like ? COLLATE NOCASE) AND (PERIOD = ? COLLATE NOCASE OR CARD_TYPE = ? COLLATE NOCASE)',
            ["%" + TRAIN_LINE + "%", PERIOD_or_CARD, PERIOD_or_CARD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Total Worked Hours per Contingent Workforce
########################################################################################################################
api = Api(blueprint_contingentworkforce, doc='/documentation', version='1.0', title='Data Service for NSW Total Hours Worked per Contingent Workforce 2019',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to Contingent Workforce YTD total hours worked per supplier in NSW.',
          )

app.register_blueprint(blueprint_contingentworkforce)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_contingentworkforce():
    sql = sqlite3.connect(path.join(ROOT, "YTDWorkedHours.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_contingentworkforce():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_contingentworkforce()
    return g.sqlite_db

@api.route('/contingentworkforce/all')
class YTDWorkedHours(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database showing Supplier, Industry, TotalHours).')
    def get(self):
        db = get_db_contingentworkforce()
        details_cur = db.execute('select Supplier, Industry, TotalHours from YTDWorkedHours')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['Supplier'] = detail['Supplier']
            detail_dict['Industry'] = detail['Industry']
            detail_dict['TotalHours'] = detail['TotalHours']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/contingentworkforce/all/<string:Industry>', methods=['GET'])
class YTDWorkedHoursIndustry(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for specific industry.')
    @api.doc(params={"Industry":'Choose from the list Education|Eligible Customers|External to GovernmentSector|Family and Community Services|Finance|Services and Innovation|Health|Industry|Justice|Planning and Environment|Premier and Cabinet|Transport|Treasury|Grand Total'})
    def get(self, Industry):
        db = get_db_contingentworkforce()
        details_cur = db.execute(
            'select Supplier, Industry, TotalHours from YTDWorkedHours where Industry = ? COLLATE NOCASE', [Industry])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['Supplier'] = detail['Supplier']
            detail_dict['Industry'] = detail['Industry']
            detail_dict['TotalHours'] = detail['TotalHours']\

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# ACNC Data
########################################################################################################################
api = Api(blueprint_acnc, doc='/documentation', version='1.0', title='Data Service for ACNC data from FY 2014 through 2017',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to charity information, compiled by the ACNC across mutliple years.',
          )

app.register_blueprint(blueprint_acnc)

#Database helper
ROOT = path.dirname(path.realpath(__file__))

def connect_db_acnc():
    sql = sqlite3.connect(path.join(ROOT, "acnc.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_acnc():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_acnc()
    return g.sqlite_db

@api.route('/all')
class CharityAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all charities and all years.')
    def get(self):
        db = get_db_acnc()
        stmt_all = """
        select
            source
            , abn
            , charity_name
            , main_activity
            , how_purposes_were_pursued
            , postcode
        from
            charities
        limit 10
        """

        details_cur = db.execute(stmt_all)
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['source'] = detail['source']
            detail_dict['abn'] = detail['abn']
            detail_dict['charity_name'] = detail['charity_name']
            detail_dict['main_activity'] = detail['main_activity']
            detail_dict['how_purposes_were_pursued'] = detail['how_purposes_were_pursued']
            detail_dict['postcode'] = detail['postcode']
            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/all/<string:abn>', methods=['GET'])
class CharityABN(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for a given charity ABN.')
    def get(self, abn):
        db = get_db_acnc()
        stmt_one = """
        select
            source
            , abn
            , charity_name
            , main_activity
            , how_purposes_were_pursued
            , postcode
            , staff___full_time
            , donations_and_bequests
        from
            charities
        where
            abn = ? collate nocase
        """

        details_cur = db.execute(stmt_one,[abn])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['source'] = detail['source']
            detail_dict['abn'] = detail['abn']
            detail_dict['charity_name'] = detail['charity_name']
            detail_dict['main_activity'] = detail['main_activity']
            detail_dict['how_purposes_were_pursued'] = detail['how_purposes_were_pursued']
            detail_dict['postcode'] = detail['postcode']
            detail_dict['staff___full_time'] = detail['staff___full_time']
            detail_dict['donations_and_bequests'] = detail['donations_and_bequests']
            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

if __name__ == '__main__':
    app.run(debug=True)
