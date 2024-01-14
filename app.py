from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from enum import Enum
from jinja2 import filters

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # Replace with your database URI
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = 'F34!8Kd9@v3m&d244xT81SPc'  # Replace with a strong, secret key

class Priority(Enum):
    VERY_LOW = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4
    CRITICAL = 5

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM)
    progress = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.completed).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    task_id = request.form.get('task_id', None)
    # Validate description
    description = request.form.get('description', '')
    if not description:
        flash('Please enter a task description.', 'error')
        return redirect(url_for('index'))
    if task_id:  # Toggling an existing task
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
    else:  # Adding a new task
        description = request.form['description']  # Ensure 'description' field is present
        new_task = Task(description=description)
        db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        # Validate description
        description = request.form['description']
        if len(description) < 4:
            flash('Task description must be at least 4 characters long.', 'error')
            return redirect(url_for('edit_task', task_id=task_id))

        # Validate priority
        try:
            priority = str(request.form['priority'])
        except ValueError:
            flash('Invalid priority value. Please enter a number.', 'error')
            return redirect(url_for('edit_task', task_id=task_id))
        
        # Update progress and completion status
        task.progress = int(request.form['progress'])
        if task.progress == 100:
            task.completed = True  # Mark as completed if progress is 100%

        if request.form.get('completed') == 'on':
            task.progress = 100  # Update progress to 100% if marked completed

        # Update other task attributes
        task.description = description
        task.completed = request.form.get('completed') == 'on'  # Already validated above
        task.priority = priority

        db.session.commit()
        return redirect(url_for('index'))

 # Pass Priority to the template
    return render_template('edit_task.html', task=task, Priority=Priority)

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.template_filter('titlecase')
def titlecase_filter(text):
    return text.replace('_', ' ').title()  # Replace underscores with spaces and capitalize

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)