import MySQLdb
import mysql.connector
from flask import Flask,redirect,render_template, request, session
#from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from random import randint
from flask_mail import Mail, Message
'''
from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
'''
app = Flask(__name__)
app.secret_key='Jenison'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gym management' 

app.config['SESSION_PERMANENT'] = False

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'gedipey@gmail.com'
app.config['MAIL_PASSWORD'] = 'tvqmjflghuilkjol'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
'''
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Gedipey852@@db.kwhttpqyehhyqvrqnevx.supabase.co:5432/postgres'

db.init_app(app)

class admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Username = db.Column(db.String, unique=True, nullable = True)
    Password = db.Column(db.Integer, nullable = False)

with app.app_context():
    db.create_all()'''    

mysql = MySQL(app)

session_active = False

nflag = False
@app.route('/verify')
def verify():
    global nflag
    nflag = True
    return render_template('verify.html') 

@app.route('/new_user')
def new_usr():
    return render_template('verify.html')

@app.route('/new_user',methods=['GET','POST'])
def new_user():
    if request.method == 'POST' and 'usname' in request.form and 'psword' in request.form:
        username = request.form['usname']
        password = request.form['psword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE Username = % s AND Password = % s', (username, password, ))
        account = cursor.fetchone()
        if account and nflag == True:
            return render_template('new_user.html')
        else:
            return render_template('verify.html', msg ='Incorrect username / password !')
    return render_template('verify.html', msg ='Incorrect username / password !')        

@app.route('/new_user_add',methods=['POST','GET'])
def new_user_add():
    if request.method == 'POST':
        username = request.form['usname']
        password = request.form['psword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT Username FROM admin WHERE Username = "{username}"')
        acc = cursor.fetchone()
        if acc == None:
            cursor.execute(f'INSERT INTO admin(Username,Password) VALUES ("{username}","{password}")')
            mysql.connection.commit()
            return render_template('new_user.html',msg='User added successfully!')
        else:
            return render_template('new_user.html',msg='User already exists')    

@app.route('/index')
def indexx():
    if 'loggedin' in session and session['loggedin']:
        return render_template('index.html',msg = session['username'])
    else:
        return redirect("/")

@app.route('/index',methods=['GET','POST'])
def index():
    msg = ''
    if request.method == 'POST' and 'usname' in request.form and 'psword' in request.form:
        username = request.form['usname']
        password = request.form['psword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE Username = %s AND Password = %s', (username, password ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['ID']
            session['username'] = account['Username']
            msg = session['username']
            global session_active
            session_active = True
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
            session_active=False
    return render_template('login.html', msg = msg)   

@app.route('/')
def login():
    if 'loggedin' in session and session['loggedin']:
        return render_template('index.html',msg=session['username'])
    else:
        return render_template('login.html')      

@app.route('/forgot_password')
def fpass():
    return render_template('f_password.html')

@app.route('/otp_validation')
def nootp():
    return render_template('login.html')

@app.route('/otp_validation',methods=['POST'])
def otp():
    usname = request.form['usname']
    email = request.form['email']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'SELECT Username FROM admin WHERE Username="{usname}"')
    acc = cursor.fetchone()
    if acc:
        session['user'] = usname
        session['email'] = email
        global otp
        otp = randint(1000,9999)
        print(otp)
        try:
            msg = Message('OTP for validation',sender ='gedipey@gmail.com',recipients = [email])
            msg.body = f'The OTP for resetting Password is {otp} \nDo not share this OTP with anyone!'
            mail.send(msg)
            return render_template('otp_page.html',msg=email)
        except Exception:
            return render_template('f_password.html',msg='Enter valid email')
    else:
        return render_template('f_password.html',msg='Username is invalid')

@app.route('/otp_resend')
def otp_resend():
    if 'email' in session and session['email']:
        global otp
        otp = randint(1000,9999)
        email = session['email']
        print(otp) 
        msg = Message('OTP for validation',sender ='gedipey@gmail.com',recipients = [email])
        msg.body = f'The OTP for resetting Password is {otp} \nDo not share this OTP with anyone!'
        mail.send(msg)
        return render_template('otp_page.html',msg=email,val='re')
    else:
        return redirect('/')    


@app.route('/otp_successful',methods=['POST'])
def otp_verification():
    user_otp = int(request.form['otp1']+request.form['otp2']+request.form['otp3']+request.form['otp4'])
    if user_otp == otp:
        return render_template('new_password.html')
    else:
        return render_template('otp_page.html',err='OTP is incorrect')


@app.route('/reset_password',methods = ['POST'])
def reset_pass():
    password = request.form['password']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'SELECT Password FROM admin WHERE Username="{session["user"]}"')
    acc = cursor.fetchone()
    if password != acc['Password']:
        usr = session['user']
        cursor.execute(f'UPDATE admin SET Password="{password}" WHERE Username="{usr}"')
        mysql.connection.commit()
        cursor.close()
        session.pop('user')
        session.pop('email')
        return render_template('successful.html')
    else:
        return render_template('new_password.html',msg='The password matches \nprevious password')

@app.route('/logout')
def logout():    
    session.pop('loggedin')
    session.pop('id')
    session.pop('username')
    global session_active
    session_active = False
    return redirect("/")

@app.route('/add_gym')
def add_gym():
    if 'loggedin' in session and session['loggedin']:
        return render_template('add_gym.html')
    else:
        return redirect("/")

@app.route('/add_gym',methods=['POST'])
def add_gym_data():
    if request.method == 'POST':    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        id = request.form['gym-id']
        name = request.form['gym-name']
        address = request.form['gym-address']
        gtype = request.form['gym-type']
        cursor.execute(f'SELECT * FROM gym WHERE Gym_ID="{id}"')
        account = cursor.fetchone()
        flag = None
        if account == None:
            cursor.execute('INSERT INTO gym(Gym_ID,Gym_Name,Address,Type) VALUES("%s","%s","%s","%s")'%(id,name,address,gtype))
            mysql.connection.commit()
            cursor.close()
            msg = "Data added successfully!"
            flag = True
            return render_template('add_gym.html', msg=msg, flag=flag)
        elif account['Gym_ID'] == id:
            flag=False
            return render_template('add_gym.html',msg = 'Gym exists', flag=flag)
        else:
            return redirect('/add_gym')    

@app.route('/view_gym')
def view_gym(): 
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM gym')
        data = cursor.fetchall()
        return render_template('view_gym.html',data=data,len=len(data))
    else:
        return redirect("/")   

@app.route('/delete_gym')
def delete_gym():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM gym')
        data = cursor.fetchall()
        return render_template('delete_gym.html',data=data,len=len(data))
    else:
        return redirect("/")

@app.route('/update_gym/<string:id>')
def update_gym(id):
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM gym WHERE Gym_ID = "{id}"')
        data = cursor.fetchone()
        return render_template('update_gym.html',data=data,len=len(data))
    else:
        redirect('/')

@app.route('/update_gym',methods=['POST'])
def update_gym_data():
    id = request.form['gym-id']
    name = request.form['gym-name']
    address = request.form['gym-address']
    gtype = request.form['gym-type']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'UPDATE gym SET Gym_Name = "{name}",Address = "{address}",Type="{gtype}" WHERE Gym_ID = "{id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM gym')
    data = cursor.fetchall()
    return render_template('delete_gym.html',data=data,len=len(data))

@app.route('/delete_gym/<string:id>')
def delete_gym_data(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'DELETE FROM gym WHERE Gym_ID = "{id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM gym')
    data = cursor.fetchall()
    return render_template('delete_gym.html')

@app.route('/add_payment')
def add_payment():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT Gym_ID FROM gym')
        res = cursor.fetchall()
        return render_template('add_payment.html',res=res)
    else:
        return redirect("/")

@app.route('/add_payment',methods = ['POST'])
def add_payment_data():
    if request.method == 'POST':
        pay_id = request.form['payment-id']
        amt = request.form['pay-amt']
        gym_id = request.form['gym-id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT Pay_ID FROM payment WHERE Pay_ID = "{pay_id}"')
        elem = cursor.fetchone()
        flag = None
        if elem == None:
            cursor.execute(f'INSERT INTO payment(Pay_ID,amount,Gym_ID) VALUES("{pay_id}","{amt}","{gym_id}")')
            mysql.connection.commit()
            cursor.close()
            flag = True
            return render_template('add_payment.html',msg = 'Data added successfully',flag=flag)
        else:
            flag = False
            return render_template('add_payment.html',msg = 'Payment Id exists',flag=flag)

@app.route('/view_payment')
def view_payment():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM payment')
        data = cursor.fetchall()
        return render_template('view_payment.html',data=data,len=len(data))
    else:
        return redirect("/") 

@app.route('/delete_payment')
def delete_payment():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM payment')
        data = cursor.fetchall()
        return render_template('delete_payment.html',data=data,len=len(data))
    else:
        return redirect("/")

@app.route('/update_payment/<string:id>')
def update_payment(id):
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM payment WHERE Pay_ID = "{id}"')
        data = cursor.fetchone()
        cursor.execute('SELECT Gym_ID FROM gym')
        gid = cursor.fetchall()
        return render_template('update_payment.html',data=data,gid=gid,len=len(data))
    else:
        redirect('/')

@app.route('/update_payment',methods=['POST'])
def update_payment_data():
    pay_id = request.form['payment-id']
    amt = request.form['pay-amt']
    gym_id = request.form['gym-id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'UPDATE payment SET amount = "{amt}",Gym_ID = "{gym_id}" WHERE Pay_ID = "{pay_id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM payment')
    data = cursor.fetchall()
    return render_template('delete_payment.html',data=data,len=len(data))


@app.route('/delete_payment/<string:id>')
def delete_payment_data(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'DELETE FROM payment WHERE Pay_ID = "{id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM payment')
    data = cursor.fetchall()
    return render_template('delete_payment.html',data=data,len=len(data))

@app.route('/add_member')
def add_member():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT Pay_ID FROM payment')
        pid = cursor.fetchall()
        cursor.execute(f'SELECT Trainer_ID FROM trainer')
        tid = cursor.fetchall()    
        return render_template('add_member.html',pid=pid,tid=tid)
    else:
        return redirect("/")    

@app.route('/add_member',methods = ['POST'])
def add_member_data():
    if request.method == 'POST':
        mem_id = request.form['member-id']
        mem_name = request.form['member-name']
        dob = request.form['date-of-birth']
        age = request.form['age']
        package = request.form['package']
        mno = request.form['mobno']
        payid = request.form['pay-id']
        trainerid = request.form['trainer-id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT Mem_ID FROM member WHERE Mem_ID = "{mem_id}"')
        elem = cursor.fetchone()
        flag = None
        if elem == None:
            cursor.execute(f'INSERT INTO member(Mem_ID,Name,Dob,Age,Package,Mobile_No,Pay_ID,Trainer_ID) VALUES("{mem_id}","{mem_name}","{dob}","{age}","{package}","{mno}","{payid}","{trainerid}")')
            mysql.connection.commit()
            cursor.close()
            flag = True
            return render_template('add_member.html',msg = 'Data added successfully',flag=flag)
        else:
            flag = False
            return render_template('add_member.html',msg = 'Member exists',flag=flag)        

@app.route('/view_members')
def view_members():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM member')
        data = cursor.fetchall()
        return render_template('view_member.html',data=data,len=len(data))
    else:
        return redirect("/")

@app.route('/delete_member')
def delete_member():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM member')
        data = cursor.fetchall()
        return render_template('delete_member.html',data=data,len=len(data))
    else:
        return redirect("/")

@app.route('/update_member/<string:id>')
def update_member(id):
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM member WHERE Mem_ID = "{id}"')
        data = cursor.fetchone()
        cursor.execute('SELECT Pay_ID FROM payment')
        pid = cursor.fetchall()
        cursor.execute('SELECT Trainer_ID FROM trainer')
        tid = cursor.fetchall()
        return render_template('update_member.html',data=data,pid=pid,tid=tid,len=len(data))
    else:
        redirect('/')

@app.route('/update_member',methods=['POST'])
def update_member_data():
    mem_id = request.form['member-id']
    mem_name = request.form['member-name']
    dob = request.form['date-of-birth']
    age = request.form['age']
    package = request.form['package']
    mno = request.form['mobno']
    payid = request.form['pay-id']
    trainerid = request.form['trainer-id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'UPDATE member SET Name = "{mem_name}",Dob = "{dob}",Age="{age}",Package="{package}",Mobile_No="{mno}",Pay_ID="{payid}",Trainer_ID="{trainerid}" WHERE Mem_ID = "{mem_id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM member')
    data = cursor.fetchall()
    return render_template('delete_member.html',data=data,len=len(data))

@app.route('/delete_member/<string:id>')
def delete_member_data(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'DELETE FROM member WHERE Mem_ID = "{id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM member')
    data = cursor.fetchall()
    return render_template('delete_member.html',data=data,len=len(data))

@app.route('/add_trainer')
def add_trainer():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Pay_ID FROM payment')
        pid = cursor.fetchall()
        return render_template('add_trainer.html',res=pid)
    else:
        return redirect("/")

@app.route('/add_trainer',methods = ['POST'])
def add_trainer_data():
    if request.method == 'POST':
        trainer_id = request.form['trainer-id']
        name = request.form['trainer-name']
        time_ = request.form['time']
        mobno = request.form['mobile-number']
        pay_id = request.form['payment-id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT Trainer_ID FROM trainer WHERE Trainer_ID = "{trainer_id}"')
        elem = cursor.fetchone()
        flag = None
        if elem == None:
            cursor.execute(f'INSERT INTO trainer(Trainer_ID,Name,Time,Mobile_No,Pay_ID) VALUES("{trainer_id}","{name}","{time_}","{mobno}","{pay_id}")')
            mysql.connection.commit()
            cursor.close()
            flag = True
            return render_template('add_trainer.html',msg = 'Data added successfully',flag=flag)
        else:
            flag = False
            return render_template('add_trainer.html',msg = 'Trainer already exists',flag=flag)

@app.route('/view_trainers')
def view_trainers():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM trainer')
        data = cursor.fetchall()
        return render_template('view_trainer.html',data=data,len=len(data))
    else:
        return redirect("/")

@app.route('/delete_trainer')
def delete_trainer():
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM trainer')
        data = cursor.fetchall()
        return render_template('delete_trainer.html',data=data,len=len(data))
    else:
        return redirect("/")

@app.route('/update_trainer/<string:id>')
def update_trainer(id):
    if 'loggedin' in session and session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM trainer WHERE Trainer_ID = "{id}"')
        data = cursor.fetchone()
        cursor.execute('SELECT Pay_ID FROM payment')
        pid = cursor.fetchall()
        return render_template('update_trainer.html',data=data,pid=pid,len=len(data))
    else:
        redirect('/')

@app.route('/update_trainer',methods=['POST'])
def update_trainer_data():
    trainer_id = request.form['trainer-id']
    name = request.form['trainer-name']
    time = request.form['time']
    mobno = request.form['mobile-number']
    pay_id = request.form['payment-id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'UPDATE trainer SET Name = "{name}",Time = "{time}",Mobile_No="{mobno}",Pay_ID="{pay_id}" WHERE Trainer_ID = "{trainer_id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM trainer')
    data = cursor.fetchall()
    return render_template('delete_trainer.html',data=data,len=len(data))


@app.route('/delete_trainer/<string:id>')
def delete_trainer_data(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'DELETE FROM trainer WHERE Trainer_ID = "{id}"')
    mysql.connection.commit()
    cursor.execute('SELECT * FROM trainer')
    data = cursor.fetchall()
    return render_template('delete_trainer.html',data=data,len=len(data))

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html',e=e),404

if __name__ == '__main__':
    app.run(debug=True)
