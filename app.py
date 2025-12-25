from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret-key"

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- MODELS ----------------
class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    description = db.Column(db.Text)

class Resource(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100))
    resource_type = db.Column(db.String(50))

class Allocation(db.Model):
    allocation_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.resource_id'))

    # Relationships to make templates easier
    event = db.relationship('Event', backref=db.backref('allocations', lazy=True))
    resource = db.relationship('Resource', backref=db.backref('allocations', lazy=True))

# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return redirect('/events')

# ---------- EVENTS ----------
@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        start = datetime.fromisoformat(request.form['start'])
        end = datetime.fromisoformat(request.form['end'])

        if start >= end:
            flash("Start time must be before end time")
            return redirect('/events')

        e = Event(
            title=request.form['title'],
            start_time=start,
            end_time=end,
            description=request.form['desc']
        )
        db.session.add(e)
        db.session.commit()
        return redirect('/events')

    return render_template('events.html', events=Event.query.all())

@app.route('/event/edit/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get(id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.start_time = datetime.fromisoformat(request.form['start'])
        event.end_time = datetime.fromisoformat(request.form['end'])
        event.description = request.form['desc']
        db.session.commit()
        return redirect('/events')
    return render_template('edit_event.html', event=event)

@app.route('/event/delete/<int:id>')
def delete_event(id):
    Event.query.filter_by(event_id=id).delete()
    db.session.commit()
    return redirect('/events')

# ---------- RESOURCES ----------
@app.route('/resources', methods=['GET', 'POST'])
def resources():
    if request.method == 'POST':
        r = Resource(
            resource_name=request.form['name'],
            resource_type=request.form['type']
        )
        db.session.add(r)
        db.session.commit()
        return redirect('/resources')

    return render_template('resources.html', resources=Resource.query.all())

@app.route('/resource/edit/<int:id>', methods=['GET', 'POST'])
def edit_resource(id):
    resource = Resource.query.get(id)
    if request.method == 'POST':
        resource.resource_name = request.form['name']
        resource.resource_type = request.form['type']
        db.session.commit()
        return redirect('/resources')
    return render_template('edit_resource.html', resource=resource)

@app.route('/resource/delete/<int:id>')
def delete_resource(id):
    Resource.query.filter_by(resource_id=id).delete()
    db.session.commit()
    return redirect('/resources')

# ---------- ALLOCATE ----------
@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    if request.method == 'POST':
        event_id = int(request.form['event'])
        resource_id = int(request.form['resource'])
        event = Event.query.get(event_id)

        # Conflict check
        conflict = db.session.query(Event).join(Allocation).filter(
            Allocation.resource_id == resource_id,
            Event.start_time < event.end_time,
            Event.end_time > event.start_time
        ).first()

        if conflict:
            flash("Conflict: Resource already booked")
            return redirect('/conflicts')

        db.session.add(Allocation(event_id=event_id, resource_id=resource_id))
        db.session.commit()
        return redirect('/allocate')

    events = Event.query.all()
    resources = Resource.query.all()
    allocations = Allocation.query.all()
    return render_template('allocate.html', events=events, resources=resources, allocations=allocations)

# ---------- CONFLICTS ----------
@app.route('/conflicts')
def conflicts():
    conflict_list = []
    allocations = Allocation.query.all()

    for a in allocations:
        e1 = Event.query.get(a.event_id)
        others = Allocation.query.filter(
            Allocation.resource_id == a.resource_id,
            Allocation.event_id != a.event_id
        ).all()

        for o in others:
            e2 = Event.query.get(o.event_id)
            if e1.start_time < e2.end_time and e1.end_time > e2.start_time:
                resource = Resource.query.get(a.resource_id)
                conflict_list.append((e1.title, e2.title, resource.resource_name))

    return render_template('conflicts.html', conflicts=conflict_list)

# ---------- REPORT ----------
@app.route('/report', methods=['GET', 'POST'])
def report():
    data = []
    if request.method == 'POST':
        start = datetime.fromisoformat(request.form['start'])
        end = datetime.fromisoformat(request.form['end'])

        for r in Resource.query.all():
            total = 0
            for a in Allocation.query.filter_by(resource_id=r.resource_id):
                e = Event.query.get(a.event_id)
                if e.start_time < end and e.end_time > start:
                    total += (min(e.end_time, end) - max(e.start_time, start)).seconds / 3600
            data.append((r.resource_name, total))

    return render_template('report.html', data=data)

# ---------- DATABASE CREATE ----------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
