from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# MySQL connection 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://...'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy objesini oluştur
db = SQLAlchemy(app)

# Meeting modeli
class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    participants = db.Column(db.String(255), nullable=False)


# Use application context to create tables before application starts
with app.app_context():
    # Create database
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/meetings', methods=['GET'])
def get_meetings():
    meetings = Meeting.query.all()
    meetings_list = []
    for meeting in meetings:
        meetings_list.append({
            'id': meeting.id,
            'topic': meeting.topic,
            'date': str(meeting.date),
            'start_time': str(meeting.start_time),
            'end_time': str(meeting.end_time),
            'participants': meeting.participants.split(',')
        })
    return jsonify(meetings_list)

@app.route('/api/meetings', methods=['POST'])
def add_meeting():
    data = request.get_json()

    new_meeting = Meeting(
        topic=data['topic'],
        date=data['date'],
        start_time=data['startTime'],
        end_time=data['endTime'],
        participants=','.join(data['participants'])
    )

    db.session.add(new_meeting)
    db.session.commit()

    return jsonify({
        'id': new_meeting.id,
        'topic': new_meeting.topic,
        'date': str(new_meeting.date),
        'start_time': str(new_meeting.start_time),
        'end_time': str(new_meeting.end_time),
        'participants': new_meeting.participants.split(',')
    })

from flask import abort

@app.route('/api/meetings/<string:topic>', methods=['PUT'])
def update_meeting_by_topic(topic):
    data = request.get_json()

    # Check if the required parameters are provided
    if 'new_topic' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    existing_meeting = Meeting.query.filter_by(topic=topic).first()

    if existing_meeting:
        existing_meeting.topic = data['new_topic']
        existing_meeting.date = data.get('new_date', existing_meeting.date)
        existing_meeting.start_time = data.get('new_start_time', existing_meeting.start_time)
        existing_meeting.end_time = data.get('new_end_time', existing_meeting.end_time)
        existing_meeting.participants = ','.join(data.get('new_participants', existing_meeting.participants.split(',')))

        db.session.commit()

        return jsonify({
            'id': existing_meeting.id,
            'topic': existing_meeting.topic,
            'date': str(existing_meeting.date),
            'start_time': str(existing_meeting.start_time),
            'end_time': str(existing_meeting.end_time),
            'participants': existing_meeting.participants.split(',')
        })
    else:
        return abort(404, description='Meeting not found')


@app.route('/api/meetings/<string:topic>', methods=['DELETE'])
def delete_meeting_by_topic(topic):
    existing_meeting = Meeting.query.filter_by(topic=topic).first()

    if existing_meeting:
        db.session.delete(existing_meeting)
        db.session.commit()

        return jsonify({
            'id': existing_meeting.id,
            'topic': existing_meeting.topic,
            'date': str(existing_meeting.date),
            'start_time': str(existing_meeting.start_time),
            'end_time': str(existing_meeting.end_time),
            'participants': existing_meeting.participants.split(',')
        })
    else:
        return jsonify({'error': 'Meeting not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
