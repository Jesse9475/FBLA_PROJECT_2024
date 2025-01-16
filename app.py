from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

#Authenticator
app = Flask(__name__)
app.secret_key = "RNX73oMEeL5ShKoaHiiZkw"

#Post database model
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

app.config['SQLALCHEMY_BINDS'] = {

    'users': 'sqlite:///users.db',
    'applications': 'sqlite:///applications.db'

}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Database model
class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(25), unique = True, nullable = False)
    is_admin = db.Column(db.Boolean, default = False)

    password_hash = db.Column(db.String(150), nullable = False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Blog model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    author = db.Column(db.String(20), nullable = False, default = 'N/A')
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return 'Blog post ' + str(self.id) 

class JobApplication(db.Model):
    __bind_key__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    cover_letter = db.Column(db.String(10000), nullable=False)
    date_applied = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    denied = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'JobApplication({self.applicant_name}, {self.position}, {self.cover_letter})'
    
all_posts = []

@app.route('/')
def index():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/posts', methods=['GET', 'POST'])
def posts():

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = BlogPost(title=post_title, content = post_content, author = post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()

    return render_template('posts.html', posts = all_posts)

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')

@app.route('/posts/edit/<int:id>', methods = ['POST'])
def edit(id):
    
    post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.author = request.form['author']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('edit.html', post = post)

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # Process form data
        applicant_name = request.form['applicant_name']
        position = request.form['position']
        cover_letter = request.form.get('cover_letter', '')  # Optional field

        new_application = JobApplication(
            applicant_name=applicant_name,
            position=position,
            cover_letter=cover_letter
        )
        db.session.add(new_application)
        db.session.commit()

        flash('Your application has been submitted successfully!', 'success')
        return redirect('/apply')  # Redirect back to the apply page or a confirmation page

    return render_template('apply.html')  # Render the application form page on GET request

#Login
@app.route("/login", methods = ['POST'])
def login():
    #Info from form
    username = request.form['username']
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error = 'Invalid username or password.')

@app.route("/register", methods = ['POST'])
def register():
    username = request.form['username']
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error = "User already here!")
    else:
        is_admin = User.query.count() == 0
        new_user = User(username = username, is_admin = is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if "username" in session:
        # Fetch the user based on the session username
        user = User.query.filter_by(username=session['username']).first()
        return render_template("dashboard.html", username=session['username'], user=user)  # Pass the 'user' object
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin(): 
    if "username" in session:
        user = User.query.filter_by(username = session['username']).first()
        if user and user.is_admin:
            return render_template("admin.html", username = user.username)
        else:
            flash("You must be admin to access this page.")
            return redirect(url_for('dashboard'))
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for('index'))
    
 #Applications Route   
@app.route('/admin/applications')
def admin_applications():
    if "username" in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.is_admin:
            # Only show unapproved applications
            unapproved_applications = JobApplication.query.filter_by(approved=False, denied=False).all()
            return render_template('admin_applications.html', applications=unapproved_applications)
        else:
            flash("You must be admin to access this page.")
            return redirect(url_for('dashboard'))
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for('index'))

#Approve Route
@app.route('/admin/applications/approve/<int:id>')
def approve_application(id):
    application = JobApplication.query.get_or_404(id)
    application.approved = True
    db.session.commit()
    return redirect('/admin/applications')

#Deny Route
@app.route('/admin/applications/deny/<int:id>')
def deny_application(id):
    application = JobApplication.query.get_or_404(id)
    application.denied = True
    db.session.commit()
    return redirect('/admin/applications')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)