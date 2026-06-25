from flask import Flask, render_template, request, make_response, redirect, session
from reportlab.pdfgen import canvas
from io import BytesIO
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "resume_builder_secret_key"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview():

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    github = request.form['github']
    linkedin = request.form['linkedin']
    template = request.form['template']

    summary = request.form['summary']
    skills = request.form['skills']
    education = request.form['education']
    projects = request.form['projects']
    experience = request.form['experience']
    certifications = request.form['certifications']

    photo = request.files['photo']

    photo_filename = ""

    if photo and photo.filename != "":
        photo_filename = secure_filename(photo.filename)

        photo.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                photo_filename
            )
        )

    return render_template(
        'preview.html',
        name=name,
        email=email,
        phone=phone,
        github=github,
        linkedin=linkedin,
        template=template,
        summary=summary,
        skills=skills,
        education=education,
        projects=projects,
        experience=experience,
        certifications=certifications,
        photo_filename=photo_filename
    )


@app.route('/download_pdf', methods=['POST'])
def download_pdf():

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    github = request.form['github']
    linkedin = request.form['linkedin']

    summary = request.form['summary']
    skills = request.form['skills']
    education = request.form['education']
    projects = request.form['projects']
    experience = request.form['experience']
    certifications = request.form['certifications']

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    y = 800

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, y, name)

    y -= 30

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Email: {email}")

    y -= 20
    pdf.drawString(50, y, f"Phone: {phone}")

    y -= 20
    pdf.drawString(50, y, f"GitHub: {github}")

    y -= 20
    pdf.drawString(50, y, f"LinkedIn: {linkedin}")

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "PROFESSIONAL SUMMARY")

    y -= 20
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, summary)

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "SKILLS")

    y -= 20
    pdf.drawString(50, y, skills)

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "EDUCATION")

    y -= 20
    pdf.drawString(50, y, education)

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "PROJECTS")

    y -= 20
    pdf.drawString(50, y, projects)

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "EXPERIENCE")

    y -= 20
    pdf.drawString(50, y, experience)

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "CERTIFICATIONS")

    y -= 20
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, certifications)

    pdf.save()

    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = (
        f'attachment; filename={name}_Resume.pdf'
    )

    return response


@app.route('/ats_score', methods=['POST'])
def ats_score():

    summary = request.form['summary']
    skills = request.form['skills']
    education = request.form['education']
    projects = request.form['projects']
    experience = request.form['experience']
    certifications = request.form['certifications']

    github = request.form['github']
    linkedin = request.form['linkedin']

    resume_text = (
        summary + " " +
        skills + " " +
        education + " " +
        projects + " " +
        experience + " " +
        certifications
    ).lower()

    keywords = [
        "python",
        "java",
        "c++",
        "sql",
        "html",
        "css",
        "javascript",
        "flask",
        "django",
        "git",
        "github",
        "machine learning",
        "data structures",
        "algorithms"
    ]

    found_keywords = []
    missing_keywords = []

    score = 0

    for keyword in keywords:

        if keyword in resume_text:
            found_keywords.append(keyword)
            score += 5
        else:
            missing_keywords.append(keyword)

    if github.strip():
        score += 10

    if linkedin.strip():
        score += 10

    if score > 100:
        score = 100

    return render_template(
        'ats_result.html',
        score=score,
        found_keywords=found_keywords,
        missing_keywords=missing_keywords
    )
@app.route('/save_resume', methods=['POST'])
def save_resume():

    if 'user_id' not in session:
      return redirect('/login')

    user_id = session['user_id']

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO resumes(
        name,email,phone,github,linkedin,
        summary,skills,education,
        projects,experience,certifications,
        user_id
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """, (

        request.form['name'],
        request.form['email'],
        request.form['phone'],
        request.form['github'],
        request.form['linkedin'],
        request.form['summary'],
        request.form['skills'],
        request.form['education'],
        request.form['projects'],
        request.form['experience'],
        request.form['certifications'],
	user_id

    ))

    conn.commit()
    conn.close()

    return """
    <h1>Resume Saved Successfully!</h1>
    <br>
    <a href='/saved_resumes'>View Saved Resumes</a>
    """


@app.route('/saved_resumes')
def saved_resumes():

    if 'user_id' not in session:
        return redirect('/login')

    search = request.args.get('search', '')

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    if search:

        cursor.execute(
            """
            SELECT * FROM resumes
            WHERE user_id=? AND name LIKE ?
            """,
            (session['user_id'], '%' + search + '%')
        )

    else:

        cursor.execute(
            """
            SELECT * FROM resumes
            WHERE user_id=?
            """,
            (session['user_id'],)
        )

    resumes = cursor.fetchall()

    conn.close()

    return render_template(
        'saved_resumes.html',
        resumes=resumes,
        search=search
    )
@app.route('/view_resume/<int:resume_id>')
def view_resume(resume_id):

    if 'user_id' not in session:
       return redirect('/login')

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM resumes WHERE id=?",
        (resume_id,)
    )

    resume = cursor.fetchone()

    conn.close()

    return render_template(
        'view_resume.html',
        resume=resume
    )
@app.route('/delete_resume/<int:resume_id>')
def delete_resume(resume_id):

    if 'user_id' not in session:
       return redirect('/login')

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM resumes WHERE id=?",
        (resume_id,)
    )

    conn.commit()
    conn.close()

    return """
    <h1>Resume Deleted Successfully!</h1>
    <br>
    <a href='/saved_resumes'>Back to Saved Resumes</a>
    """
@app.route('/edit_resume/<int:resume_id>')
def edit_resume(resume_id):

    if 'user_id' not in session:
       return redirect('/login')

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM resumes WHERE id=?",
        (resume_id,)
    )

    resume = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_resume.html',
        resume=resume
    )
@app.route('/update_resume/<int:resume_id>', methods=['POST'])
def update_resume(resume_id):

    if 'user_id' not in session:
       return redirect('/login')

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE resumes
    SET
        name=?,
        email=?,
        phone=?,
        github=?,
        linkedin=?,
        summary=?,
        skills=?,
        education=?,
        projects=?,
        experience=?,
        certifications=?
    WHERE id=?
    """, (

        request.form['name'],
        request.form['email'],
        request.form['phone'],
        request.form['github'],
        request.form['linkedin'],
        request.form['summary'],
        request.form['skills'],
        request.form['education'],
        request.form['projects'],
        request.form['experience'],
        request.form['certifications'],
        resume_id

    ))

    conn.commit()
    conn.close()

    return """
    <h1>Resume Updated Successfully!</h1>
    <br>
    <a href='/saved_resumes'>Back to Saved Resumes</a>
    """
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users(username,email,password)
        VALUES(?,?,?)
        """, (username, email, password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users
        WHERE email=? AND password=?
        """, (email, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/dashboard')

        return "<h1>Invalid Login Credentials</h1>"

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM resumes WHERE user_id=?",
        (session['user_id'],)
    )

    total_resumes = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT name
        FROM resumes
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 5
        """,
        (session['user_id'],)
    )

    recent_resumes = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        total_resumes=total_resumes,
        recent_resumes=recent_resumes
    )


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)