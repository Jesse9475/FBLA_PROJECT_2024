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

#Model for Blog Posts
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())

    # Additional fields to store job application data
    applicant_name = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    salary = db.Column(db.Integer, nullable=True)
    jobType = db.Column(db.String, nullable=True)  # Correct column name
    experienceLevel = db.Column(db.String, nullable=True)  # Correct column name
    remoteOnly = db.Column(db.String, nullable=True)  # Correct column name

    def __repr__(self):
        return f'Blog post {self.id}'


class JobApplication(db.Model):
    __bind_key__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    cover_letter = db.Column(db.String(10000), nullable=False)
    date_applied = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
    approved = db.Column(db.Boolean, nullable=False, default=False)
    denied = db.Column(db.Boolean, nullable=False, default=False)
    username_author = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=True)
    jobType = db.Column(db.String, nullable = True)
    experienceLevel = db.Column(db.String, nullable = True)
    remoteOnly = db.Column(db.String, nullable = True)
    def __repr__(self):
        return f'JobApplication({self.applicant_name}, {self.position}, {self.cover_letter})'
    

@app.route('/landingpage')
def index():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/posts', methods=['GET', 'POST'])
@app.route('/posts', methods=['GET', 'POST'])
def posts():
    salary_min = None
    salary_max = None

    salary_range = request.args.get('salary_range')
    job_type = request.args.get('job_type')
    experience_level = request.args.get('experience_level')
    remote_only = request.args.get('remote_only')

    if salary_range:
        if salary_range == "0-50000":
            salary_min, salary_max = 0, 50000
        elif salary_range == "50000-100000":
            salary_min, salary_max = 50000, 100000
        elif salary_range == "100000+":
            salary_min, salary_max = 100000, None

    if request.method == 'POST':
        post_title = request.form['applicant_name']
        post_content = request.form['cover_letter']
        post_author = request.form['position']
        post_salary = int(request.form['salary'])  # Convert to integer
        post_type = request.form['jobType']
        post_experience = request.form['experienceLevel']
        post_remote = request.form['remoteOnly']

        new_post = BlogPost(
            title=post_title,
            content=post_content,
            author=post_author,
            salary=post_salary,
            jobType=post_type,
            experienceLevel=post_experience,
            remoteOnly=post_remote
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect('/posts')

    query = BlogPost.query
    
    if salary_min is not None:
        query = query.filter(BlogPost.salary >= salary_min)
    if salary_max is not None:
        query = query.filter(BlogPost.salary <= salary_max)
    if job_type:
        query = query.filter(BlogPost.jobType == job_type)
    if experience_level:
        query = query.filter(BlogPost.experienceLevel == experience_level)
    if remote_only:
        query = query.filter(BlogPost.remoteOnly == remote_only)

    all_posts = query.order_by(BlogPost.date_posted).all()

    return render_template('what.html', posts=all_posts)

# @app.route('/posts/delete/<int:id>')
# def delete(id):
#     post = BlogPost.query.get_or_404(id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect('/posts')

# @app.route('/posts/edit/<int:id>', methods = ['POST'])
# def edit(id):
    
#     post = BlogPost.query.get_or_404(id)
#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.content = request.form['content']
#         post.author = request.form['author']
#         db.session.commit()
#         return redirect('/posts')
#     else:
#         return render_template('edit.html', post = post)

@app.route('/create_job_posting', methods=['GET', 'POST'])
def apply():
    if "username" not in session:
        flash("You must be logged in to apply!", "warning")
        return redirect('/')

    if request.method == 'POST':
        # Process form data
        username_author = session['username']
        applicant_name = request.form['applicant_name']
        position = request.form['position']
        salary = int(request.form['salary'])  # Convert to integer
        cover_letter = request.form.get('cover_letter', '')  # Optional field
        jobType = request.form['jobType']
        experienceLevel = request.form['experienceLevel']
        remoteOnly = request.form['remoteOnly']

        new_application = JobApplication(
            username_author=username_author,
            applicant_name=applicant_name,
            position=position,
            cover_letter=cover_letter,
            salary=salary,
            jobType=jobType,
            experienceLevel=experienceLevel,
            remoteOnly=remoteOnly
        )
        db.session.add(new_application)
        db.session.commit()
    
        flash('Your application has been submitted successfully!', 'success')
        return redirect('/create_job_posting')  # Redirect back to the apply page or a confirmation page

    return render_template('add-listing.html')  # Render the application form page on GET request

#Login
@app.route("/login", methods = ['GET', 'POST'])
def login():
    #Info from form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return render_template('login.html', error = 'Invalid username or password.')
    return render_template('login.html')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
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
    return render_template('register.html')

@app.route("/dashboard")
def dashboard():
    if "username" in session:
        # Fetch the user based on the session username
        user = User.query.filter_by(username=session['username']).first()
        return render_template("homepage.html", username=session['username'], user=user)  # Pass the 'user' object
    return redirect(url_for('index'))

@app.route("/")
def homepage():
    return render_template("landingpage.html")

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

    # Mark the application as approved
    application.approved = True
    db.session.commit()

    # Create a new BlogPost entry based on the approved application
    new_post = BlogPost(
        title=application.applicant_name,
        content=application.cover_letter,
        author= application.username_author,
        applicant_name=application.applicant_name,
        position=application.position,
        cover_letter=application.cover_letter,
        salary=application.salary,
        jobType=application.jobType,
        experienceLevel=application.experienceLevel,
        remoteOnly=application.remoteOnly
    )
    db.session.add(new_post)
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