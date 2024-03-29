#
# from flask import Flask , render_template ,request
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from sqlalchemy import databases
#
#
#
# app=Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/xmotive'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']='False'
# db = SQLAlchemy(app)
#
# class Contacts(db.Model):
#     sno= db.Column(db.Integer, primary_key=True)
#     name= db.Column(db.String(80), unique=False)
#     email= db.Column(db.String(20), unique=True)
#     ph_num= db.Column(db.String(12), unique=True)
#     msg= db.Column(db.String(80))
#     date= db.Column(db.String(12) ,nullable=True)
#
#
# @app.route("/")
# def index():
#     return  render_template('index.html')
#
# @app.route("/index")
# def home():
#     return  render_template('index.html')
#
# @app.route("/about")
# def about():
#     return render_template('about.html')
#
# @app.route("/post")
# def post():
#     return render_template('post.html')
#
# @app.route("/contact" ,methods=['GET','POST'])
# def contact():
#     if(request.method=='POST'):
#         '''ADD entery to the database'''
#         name=request.form.get('name')
#         email=request.form.get('email')
#         phone=request.form.get('phone')
#         message=request.form.get('message')
#         #apede deta fetch kari lidho have ane data base ma nakhavano
#
#         entry=Contacts(name=name,email=email,ph_num=phone,msg=message,date=datetime.now())
#         db.session.add(entry)
#         db.session.commit()
#
#     return render_template('contact.html')
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import  json
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import  math






with open('config.json','r') as c:
    params=json.load(c)["params"]

local_server=True
app = Flask(__name__)
app.secret_key="akshar-bhalani"
db = SQLAlchemy(app)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gamil-password']
)

app.config['UPLOAD_FOLDER']=params['upload_location']








mail=Mail(app)







if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']



class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    ph_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_post']))
    page=request.args.get('page')
    if (not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_post']):(page-1)*int(params['no_post'])+int(params['no_post'])]
    #logic of pegination

    #-->first page
    if page==1:
        prev="#"
        next="/?page" + str(page+1)

    elif page==last:
        next = "#"
        prev= "/?page" + str(page + 1)
    else:
        prev = "/?page" + str(page - 1)
        next = "/?page" + str(page + 1)

    #prev=0
    #next=page+1
    #---->middel page
    #prev=page-1
    #next=page+1
    #last
    #prev=page-1
    #next=0



    return render_template('index.html',params=params,posts=posts,prev=prev,next=next )


@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post =Posts.query.filter_by(slug=post_slug).first()




    return render_template('post.html',params=params,post=post)







@app.route("/index")
def index():
    return  render_template('index.html',params=params)

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if "user" in session and session['user'] == params['admin_user']:
        if request.method=="POST":
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "uploaded sucsses"



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user'] == params['admin_user']:

        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return  redirect('/dashboard')








@app.route("/dashboard",methods=['GET','POST'])
def dashboard():

    if "user" in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    if request.method=="POST":
        username=request.form.get("uname")
        userpass = request.form.get("pass")
        if username==params['admin_user'] and userpass == params['admin_pass']:
            session['user']=username
            posts=Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
    else:
        return render_template('login.html',params=params)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    print("jel")
    if "user" in session and session['user'] == params['admin_user']:
        if request.method=='POST':
            box_title=request.form.get('title')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()

            if sno=='0':

                post=Posts(title=box_title,slug=slug,content=content,img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post)



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name,email = email ,ph_num = phone, msg = message, date= datetime.now()  )





        db.session.add(entry)
        db.session.commit()

        mail.send_message('New massge from' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body= message + "\n" + phone





                          )


    return render_template('contact.html',params=params)

if __name__ == '__main__':
    app.run(debug=True)


