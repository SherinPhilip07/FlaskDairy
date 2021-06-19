from flask import Flask, render_template,request,redirect
from models import db,login,UserModel,Entry
from flask_login import login_required,current_user,login_user,logout_user
from datetime import datetime
from logging import FileHandler,WARNING
 
app = Flask(__name__)
app.secret_key = 'xyz'

file_handler=FileHandler('error.txt')
file_handler.setLevel(WARNING)
app.logger.addHandler(file_handler)
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlitedb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
 
db.init_app(app)
login.init_app(app)
login.login_view = 'login'

 
@app.before_first_request
def create_all():
    db.create_all()
 
@app.route('/add',methods = ['POST', 'GET'])
@login_required

def add():
    email = current_user.email
    if request.method == 'POST':      
        title = request.form['title']
        content = request.form['content']
        date=datetime.now()
        entry = Entry(email=email, title=title, content=content,date_posted=date)
        db.session.add(entry)
        db.session.commit()        
        return redirect('/add')   
    return render_template('blog.html')

@app.route('/view',methods = ['POST', 'GET'])
@login_required
def view():
     email = current_user.email
     result = Entry.query.filter_by(email = email)
     result = sorted(result,key=lambda x:x.date_posted,reverse=True)
     return render_template('view.html',result=result)
    
@app.route('/del/<int:pid>')
@login_required
def delete(pid):
    res=Entry.query.filter_by(pid=pid).delete()
    db.session.commit()
    return redirect('/view')

@app.route('/edit/<int:pid>',methods = ['POST', 'GET'])
@login_required
def edit(pid):
    post=Entry.query.get(pid)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.date=datetime.now()
        db.session.commit()
        return redirect('/view')
    return render_template('edit.html',post=post)   
    
    

@app.route('/login', methods = ['POST', 'GET'])
def login():    
    if current_user.is_authenticated:
        return redirect('/add')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()


        if not email:
            error="All fields required"
            return render_template('login.html',error=error)        
        
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/add')
        else:
            return ("Password is incorrect")
            
    return render_template('login.html')
 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/add')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if not email or not username or not password:
            error="All fields required"
            return render_template('register.html',error=error)
     
        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    
    return render_template('register.html')

@app.errorhandler(404)
def pafe_not_found(e):
    return render_template("404.html") 
                
 
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/add')

app.run()
