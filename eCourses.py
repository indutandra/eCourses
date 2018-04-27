from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy import Table, DateTime, desc
import datetime
import sys
from datetime import datetime
# from app import db

app = Flask(__name__)

app.config['SECRET_KEY'] = 'eCourses'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogDataBase.db'
ALLOWED_EXTENSIONS = set(['txt', 'pdf','png', 'jpg', 'jpeg', 'gif','JPG','JPEG','mp4'])

db=SQLAlchemy(app)

class LoginDetails(db.Model):
	__tablename__='accounts'
	email = db.Column(db.String(100), primary_key=True)
	name = db.Column(db.String(200))
	password = db.Column(db.String(240))
	phone = db.Column(db.String(20))

	def __init__(self, name, email, password, phone):
		self.email = email
		self.name = name
		self.password = password
		self.phone = phone

	def __repr__(self):
		return '<Entry\nEmail Id: %r\nName: %r\nPassword: %r\nPhone number: %r\n>' % (self.email, self.name, self.password, self.phone)

class blogsDB(db.Model):
	__tablename__ = 'blogs'
	sno = db.Column(db.Integer, autoincrement = True, primary_key=True)
	blog_postedBy = db.Column(db.String(200))
	blog_postedAt = db.Column(db.DateTime)
	blog_Title = db.Column(db.String(100))
	blog_Message = db.Column(db.String(1000))
	blog_likes = db.Column(db.Integer)

	def __init__(self,blog_postedBy,blog_postedAt,blog_Title,blog_Message,blog_likes):
		self.blog_postedBy = blog_postedBy
		self.blog_postedAt = blog_postedAt
		self.blog_Title = blog_Title
		self.blog_Message = blog_Message
		self.blog_likes = blog_likes

	def __repr__(self):
		return '<Entry\nposted_By: %r\ntime: %r\nTitle: %r\nMessage: %r\nlikes: %r\n>' % (self.blog_postedBy, self.blog_postedAt, self.blog_Title, self.blog_Message, self.blog_likes)

db.create_all()

def authenticate(e, p):
	details=LoginDetails.query.filter_by(email=e).all()
	if(len(details)>0):
		if details[0].password==p:
			return ""
		else: return "Incorrect Password"
	return "No Email exists"

def authenticateEmail(e):
	details=LoginDetails.query.filter_by(email=e).all()
	if(len(details)>0):
		return False
	return True

@app.route('/postBlog', methods=['GET', 'POST'])
def postBlog():
	if request.method == 'POST':
		blog_Title = request.form['blog_Title']
		blog_Message = request.form['blog_Message']
		blog_by = LoginDetails.query.filter_by(email=session['log_email']).all()[0].name
		print (blog_by)
		new_blog = blogsDB(blog_postedBy = blog_by,blog_postedAt=datetime.now(), blog_Title = blog_Title, blog_Message = blog_Message, blog_likes = 0)
		db.session.add(new_blog)
		db.session.commit()
		blogs_so_far = reversed(blogsDB.query.all())
		return render_template('forums.html',blogs_so_far=blogs_so_far)
	return render_template('postBlog.html')

@app.route('/forums',methods=['GET','POST'])
def forums():
	if request.method == 'POST':
		(blog_sno, votetype) = (request.form['vote'].split()[0],request.form['vote'].split()[1])
		blog = blogsDB.query.filter_by(sno = blog_sno).all()[0]
		if votetype == "upvote":
			blog.blog_likes+=1
			db.session.commit()
		elif votetype == "downvote":
			blog.blog_likes-=1
			db.session.commit()
		return redirect(url_for('forums'))
	blogs_so_far = reversed(blogsDB.query.all())
	return render_template('forums.html', blogs_so_far = blogs_so_far)

@app.route('/', methods=['GET', 'POST'])
def Main():
	if request.method == 'POST':
		(blog_sno, votetype) = (request.form['vote'].split()[0],request.form['vote'].split()[1])
		blog = blogsDB.query.filter_by(sno = blog_sno).all()[0]
		if votetype == "upvote":
			blog.blog_likes+=1
			db.session.commit()
		elif votetype == "downvote":
			blog.blog_likes-=1
			db.session.commit()
		return redirect(url_for('Main'))
	blogs_so_far = reversed(blogsDB.query.all())
	return render_template('Main.html', blogs_so_far = blogs_so_far)

@app.route('/sign/<name>/<mail>')
def sign(name,mail):
	# blogs_so_far = reversed(blogsDB.query.all())
	print ("entered")
	print (name) 
	print (mail)
	stmt = "SELECT email FROM accounts"
	data = db.engine.execute(stmt).fetchall()
	for x in data:
		print (x.email)
		if mail != x.email	:
			print ("mail not in data and session True")
			newUser = LoginDetails(email=mail,name=name,password=None,phone=None)
			db.session.add(newUser)
			db.session.commit()
			session['logged_in'] = True
			session['log_email'] = mail
			return redirect(url_for('Main'))
		else:
			session['logged_in'] = True
			session['log_email'] = mail
			return redirect(url_for('Main'))

@app.route('/login', methods=['GET', 'POST'])
def Login():
	error = None
	if request.method == 'POST':
		error = (authenticate(request.form['email'], request.form['password']))
		if error=="":
			session['logged_in'] = True
			session['log_email'] = request.form['email']
			flash("You are logged in")
			return redirect(url_for('Main'))
		return render_template('Login.html', error=error)
	try:
		if session['logged_in']==True:
			return redirect('/')
	except:
		return render_template('Login.html', error="")
	return render_template('Login.html', error="")

@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('Main'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	error = None
	if request.method == 'POST':
		if(authenticateEmail(request.form['email'])):
			if request.form['password'] != request.form['rePassword']:
				error = 'Re-enter password'
			else:
				newUser = LoginDetails(email=request.form['email'],name=request.form['name'],password=request.form['password'],phone=request.form['phone'])
				db.session.add(newUser)
				print(newUser)
				db.session.commit()
				return redirect(url_for('Login'))
			return render_template('signup.html', error=error)
		else:
			error = 'The Email Id entered is already registered!!'
			return render_template('signup.html', error=error)
	try:
		if session['logged_in']==True:
			return redirect('/')
	except:
		return render_template('signup.html', error="")
	return render_template('signup.html', error="")
	
@app.route('/userdetails')
def userdetails():
	# try:
		if session['logged_in']==True:
			print ("session logged_in")
			customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		return render_template('userdetails.html',customer=customer)
		# return redirect(url_for('Login'))
	# except:
	# 	return redirect(url_for('Login'))

@app.route('/courses')
def courses():
	try:
		if session['logged_in']==True:
			customer = LoginDetails.query.filter_by(email=session['log_email']).one()
			return render_template('courses.html',customer=customer)
		return redirect(url_for('Login'))
	except:
		return redirect(url_for('Login'))

@app.route('/python',methods=['POST','GET'])
def python():
	try:
		if session['logged_in']==True:
			print ("session entered")
			customer = LoginDetails.query.filter_by(email=session['log_email']).one()
			x="Lesson1.mp4"
			c=5010
			thispath = "python"
			return render_template('python_courses.html')
			# return render_template('python.html',customer=customer,name=x,port=c,path=thispath)
		return redirect(url_for('Login'))
	except:
		print ("session Not entered")
		return redirect(url_for('Login'))

@app.route('/py_Lesson/1/1')
def py_Lesson1():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson1.mp4"
		c=5010
		thispath = "py_Lesson/1/1"
		return render_template('python_videos.html',customer=customer,name=x,port=c,path=thispath)

@app.route('/py_Lesson/1/2')
def py_Lesson2():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson2.mp4"
		c=5010
		thispath = "py_Lesson/1/2"
		return render_template('python_videos.html',customer=customer,name=x,port=c,path=thispath)


# 000000000000000000000000000000000000000000000000000000000000000000000000000000000

@app.route('/java',methods=['POST','GET'])
def java():
	try:
		if session['logged_in']==True:
			print ("session entered")
			customer = LoginDetails.query.filter_by(email=session['log_email']).one()
			x="Lesson5.mp4"
			c=5010
			thispath = "java"
			return render_template('java_courses.html')
			# return render_template('python.html',customer=customer,name=x,port=c,path=thispath)
		return redirect(url_for('Login'))
	except:
		print ("session Not entered")
		return redirect(url_for('Login'))

@app.route('/java_Lesson/1/5')
def java_Lesson5():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson5.mp4"
		c=5010
		thispath = "java_Lesson/1/5"
		return render_template('java_videos.html',customer=customer,name=x,port=c,path=thispath)

@app.route('/java_Lesson/1/6')
def java_Lesson6():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson6.mp4"
		c=5010
		thispath = "java_Lesson/1/6"
		return render_template('java_videos.html',customer=customer,name=x,port=c,path=thispath)


# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

@app.route('/ml',methods=['POST','GET'])
def ml():
	try:
		if session['logged_in']==True:
			print ("session entered")
			customer = LoginDetails.query.filter_by(email=session['log_email']).one()
			x="Lesson9.mp4"
			c=5010
			thispath = "ml"
			return render_template('ml_courses.html')
			# return render_template('python.html',customer=customer,name=x,port=c,path=thispath)
		return redirect(url_for('Login'))
	except:
		print ("session Not entered")
		return redirect(url_for('Login'))

@app.route('/ml_Lesson/1/9')
def ml_Lesson9():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson9.mp4"
		c=5010
		thispath = "ml_Lesson/1/9"
		return render_template('ml_videos.html',customer=customer,name=x,port=c,path=thispath)

@app.route('/ml_Lesson/1/10')
def ml_Lesson10():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson10.mp4"
		c=5010
		thispath = "ml_Lesson/1/10"
		return render_template('ml_videos.html',customer=customer,name=x,port=c,path=thispath)

# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

@app.route('/wp',methods=['POST','GET'])
def wp():
	try:
		if session['logged_in']==True:
			print ("session entered")
			customer = LoginDetails.query.filter_by(email=session['log_email']).one()
			x="Lesson13.mp4"
			c=5010
			thispath = "wp"
			return render_template('wp_courses.html')
			# return render_template('python.html',customer=customer,name=x,port=c,path=thispath)
		return redirect(url_for('Login'))
	except:
		print ("session Not entered")
		return redirect(url_for('Login'))

@app.route('/wp_Lesson/1/13')
def wp_Lesson13():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson13.mp4"
		c=5010
		thispath = "wp_Lesson/1/13"
		return render_template('wp_videos.html',customer=customer,name=x,port=c,path=thispath)

@app.route('/wp_Lesson/1/14')
def wp_Lesson14():
	if session['logged_in']==True:
		print ("session entered")
		customer = LoginDetails.query.filter_by(email=session['log_email']).one()
		x="Lesson14.mp4"
		c=5010
		thispath = "wp_Lesson/1/14"
		return render_template('wp_videos.html',customer=customer,name=x,port=c,path=thispath)

# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000



if __name__ == '__main__':
	app.run()
