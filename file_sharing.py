from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

UPLOAD_FOLDER = 'uploads'
STUDENTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'STUDENTS')
TEACHERS_FOLDER = os.path.join(UPLOAD_FOLDER, 'TEACHERS')
YEAR_7_FOLDER = os.path.join(STUDENTS_FOLDER, 'YEAR_7')
YEAR_8_FOLDER = os.path.join(STUDENTS_FOLDER, 'YEAR_8')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STUDENTS_FOLDER, exist_ok=True)
os.makedirs(YEAR_7_FOLDER, exist_ok=True)
os.makedirs(YEAR_8_FOLDER, exist_ok=True)
os.makedirs(TEACHERS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define user credentials
USERS = {
    'admin': {'password': 'password123', 'role': 'admin'},
    'teacher': {'password': 'teacherpass', 'role': 'Teacher'},
    'student_year_7': {'password': 'student7pass', 'role': 'Student', 'Year': 'YEAR_7'},
    'student_year_8': {'password': 'student8pass', 'role': 'Student', 'Year': 'YEAR_8'}
}

@app.route('/')
def index():
    role = session.get('role')

    if not role:
        return redirect(url_for('login'))

    student_files_year_7 = os.listdir(YEAR_7_FOLDER)
    student_files_year_8 = os.listdir(YEAR_8_FOLDER)
    teacher_files = os.listdir(TEACHERS_FOLDER)

    student_files = []
    welcome_message = ""

    if role == 'Student':
        if session.get('Year') == 'YEAR_7':
            student_files = student_files_year_7
            welcome_message = "WELCOME YEAR 7 STUDENT"
        elif session.get('Year') == 'YEAR_8':
            student_files = student_files_year_8
            welcome_message = "WELCOME YEAR 8 STUDENT"
    elif role == 'admin':
        student_files = student_files_year_7 + student_files_year_8
        welcome_message = "WELCOME ADMIN"

    return render_template('index.html', 
                           student_files_year_7=student_files_year_7,
                           student_files_year_8=student_files_year_8,
                           teacher_files=teacher_files, 
                           role=role,
                           welcome_message=welcome_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)

        if user and user['password'] == password:
            session['role'] = user['role']
            session['Year'] = user.get('Year')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('role', None)
    session.pop('Year', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    file = request.files.get('file')
    target_group = request.form.get('target_group')
    year_group = request.form.get('year_group')

    if not file or file.filename == '' or not target_group:
        return redirect(request.url)

    save_folder = TEACHERS_FOLDER if target_group == 'Teachers' else YEAR_7_FOLDER if year_group == 'YEAR_7' else YEAR_8_FOLDER
    os.makedirs(save_folder, exist_ok=True)  # Ensure folder exists

    file_path = os.path.join(save_folder, file.filename)
    file.save(file_path)

    return redirect(url_for('index'))

@app.route('/download/<user_type>/<filename>')
def download_file(user_type, filename):
    year_group = request.args.get('year_group')
    folder = TEACHERS_FOLDER if user_type == 'Teacher' else YEAR_7_FOLDER if year_group == 'YEAR_7' else YEAR_8_FOLDER
    return send_from_directory(folder, filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    for folder in [TEACHERS_FOLDER, YEAR_7_FOLDER, YEAR_8_FOLDER]:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
