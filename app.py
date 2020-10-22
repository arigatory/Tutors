import os
from flask import Flask
from flask import render_template
from flask import request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField
from wtforms.validators import InputRequired, Length

import data_provider

app = Flask(__name__)
app.secret_key = '42'

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

print(app.config["SQLALCHEMY_DATABASE_URI"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут", [InputRequired(message="Данное поле являетвся обязательным"),
                                           Length(min=2, message='Слишком короткое имя')])
    clientPhone = StringField("Ваш телефон", [InputRequired(message="Данное поле являетвся обязательным"),
                                              Length(min=5, message='Слишком короткий номер телефона')])
    submit = SubmitField("Записаться на пробный урок")
    clientWeekday = HiddenField("mon")
    clientTime = HiddenField("12:00")
    clientTeacher = HiddenField("10")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    weekday = db.Column(db.String(20))
    hour = db.Column(db.Integer)
    teacher = db.relationship("Teacher", back_populates='bookings')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    goal = db.Column(db.String(20))
    free_time = db.Column(db.String(20))


teachers_goals_association = db.Table('teachers_goals',
                                      db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
                                      db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'))
                                      )


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    picture = db.Column(db.String())
    about = db.Column(db.String())
    price = db.Column(db.Integer())
    rating = db.Column(db.Float())
    bookings = db.relationship("Booking", back_populates='teacher')
    free_times = db.relationship('FreeTimes', back_populates='teacher')
    goals = db.relationship('Goal', secondary=teachers_goals_association, back_populates='teachers')


class FreeTimes(db.Model):
    __tablename__ = 'free_times'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time)
    weekday = db.Column(db.String)
    teacher = db.relationship("Teacher", back_populates='free_times')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    rus = db.Column(db.String)
    short = db.Column(db.String)
    teachers = db.relationship('Teacher', secondary=teachers_goals_association, back_populates='goals')


class RequestForm(FlaskForm):
    clientName = StringField("Вас зовут", [InputRequired(message="Данное поле являетвся обязательным"),
                                           Length(min=2, message='Слишком короткое имя')])
    clientPhone = StringField("Ваш телефон", [InputRequired(message="Данное поле являетвся обязательным"),
                                              Length(min=5, message='Слишком короткий номер телефона')])
    submit = SubmitField("Найти мне преподавателя")
    goals = Goal.query.all()
    choices = []
    for goal in goals:
        choices.append((goal.short, goal.rus))
    goal = RadioField("Какая цель занятий?", choices=choices, default='travel')
    free_time = RadioField("Сколько времени есть?", choices=[('1-2', '1-2 часа в неделю'),
                                                             ('3-5', '3-5 часов в неделю'),
                                                             ('5-7', '5-7 часов в неделю'),
                                                             ('7-10', '7-10 часов в неделю')], default='3-5')


@app.route('/')
def render_main():
    teachers = Teacher.query.order_by(func.random()).limit(6).all()
    goals = Goal.query.all()
    return render_template('index.html', goals=goals, teachers=teachers)


@app.route('/all/')
def render_all():
    teachers = Teacher.query.all()
    goals = Goal.query.all()
    return render_template('index.html', goals=goals, teachers=teachers)


@app.route('/goals/<goal>/')
def render_goals(goal):
    goals = Goal.query.all()
    goal = Goal.query.filter(Goal.short == goal).first()
    teachers = Teacher.query.filter(Teacher.goals.contains(goal)).all()
    return render_template('goal.html', goals=goals, goal=goal, teachers=teachers)


@app.route('/profiles/<int:teacher_id>/')
def render_profiles(teacher_id):
    teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
    week = data_provider.whole_week()
    return render_template('profile.html', teacher=teacher, goals=teacher.goals, week=week)


@app.route('/request/', methods=['GET', 'POST'])
def render_request():
    form = RequestForm()
    if request.method == "POST" and form.validate():
        name = form.clientName.data
        phone = form.clientPhone.data
        goal = form.goal.data
        choices = dict(form.goal.choices)
        goal_label = choices[goal]
        free_time = form.free_time.data
        choices = dict(form.free_time.choices)
        free_time_label = choices[free_time]
        req = Request(name=name, phone=phone, goal=goal, free_time=free_time)
        db.session.add(req)
        db.session.commit()
        return render_template('request_done.html', name=name, phone=phone, goal=goal_label, free_time=free_time_label)
    else:
        return render_template('request.html', form=form)


@app.route('/booking/<int:teacher_id>/<day_of_the_week>/<int:time>/', methods=['GET', 'POST'])
def render_booking(teacher_id, day_of_the_week, time):
    teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
    week = data_provider.whole_week()
    form = BookingForm()

    if request.method == "POST" and form.validate():
        name = form.clientName.data
        weekdays = data_provider.whole_week()
        weekday = weekdays[form.clientWeekday.data]
        time = form.clientTime.data
        phone = form.clientPhone.data
        booking = Booking(weekday=weekday, hour=time, name=name, phone=phone, teacher_id=teacher_id)
        db.session.add(booking)
        db.session.commit()
        # data_provider.save_booking(booking)
        return render_template('booking_done.html', name=name, weekday=weekday, time=time, phone=phone)
    else:
        return render_template('booking.html', teacher=teacher, day_of_the_week=day_of_the_week, time=time, week=week,
                               form=form)


@app.route('/booking_done/', methods=["GET", "POST"])
def render_booking_done():
    form = BookingForm()

    if form.validate_on_submit():
        return "OK"
    else:
        return "errors"


if __name__ == '__main__':
    app.run()
