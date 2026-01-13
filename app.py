from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os, csv

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///work.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/screenshots'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Model
class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    screenshot = db.Column(db.String(300))

# ✅ Flask 3.x FIX
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    works = Work.query.order_by(Work.id.desc()).all()
    return render_template('dashboard.html', works=works)

@app.route('/add', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        screenshot = request.files.get('screenshot')
        filename = None

        if screenshot and screenshot.filename:
            filename = secure_filename(screenshot.filename)
            screenshot.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        work = Work(
            task=request.form['task'],
            details=request.form['details'],
            status=request.form['status'],
            start_time=datetime.fromisoformat(request.form['start_time']),
            end_time=datetime.fromisoformat(request.form['end_time']),
            screenshot=filename
        )
        db.session.add(work)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('add_work.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_work(id):
    work = Work.query.get_or_404(id)

    if request.method == 'POST':
        work.task = request.form['task']
        work.details = request.form['details']
        work.status = request.form['status']
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_work.html', work=work)

@app.route('/report')
def report():
    return render_template('report.html', works=Work.query.all())

@app.route('/download')
def download():
    filename = 'work_report.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Task', 'Details', 'Status', 'Start', 'End'])
        for w in Work.query.all():
            writer.writerow([w.task, w.details, w.status, w.start_time, w.end_time])
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
