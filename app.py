from flask import Flask
from flask import render_template

from flask_wtf import FlaskForm
from jinja2 import environment
from wtforms import StringField, SubmitField, HiddenField

import data_provider

app = Flask(__name__)
app.secret_key = '42'


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут")
    clientPhone = StringField("Ваш телефон")
    submit = SubmitField("Записаться на пробный урок")
    clientWeekday = HiddenField("mon")
    clientTime = HiddenField("12:00")
    clientTeacher = HiddenField("10")


class Booking:
    def __init__(self, weekday, hour, name, phone):
        self.weekday = weekday
        self.hour = hour
        self.name = name
        self.phone = phone


@app.route('/')
def render_main():
    return render_template('index.html', goals=data_provider.get_goals(), teachers=data_provider.get_teachers(6))

@app.route('/all/')
def render_all():
    return render_template('index.html', goals=data_provider.get_goals(), teachers=data_provider.get_teachers())


@app.route('/goals/<goal>/')
def render_goals(goal):
    goals = data_provider.get_goals()
    teachers = data_provider.get_teachers()
    return render_template('goal.html', goals=goals, goal=goal, teachers=teachers)


@app.route('/profiles/<int:teacher_id>/')
def render_profiles(teacher_id):
    teacher = data_provider.get_teacher(teacher_id)
    goals = [data_provider.get_goal(k) for k in teacher['goals']]
    week = data_provider.whole_week()
    return render_template('profile.html', teacher=teacher, goals=goals, week=week)


@app.route('/request/')
def render_request():
    return render_template('request.html')


@app.route('/request_done/')
def render_request_done():
    return render_template('request_done.html')


@app.route('/booking/<int:teacher_id>/<day_of_the_week>/<time>/', methods=['GET', 'POST'])
def render_booking(teacher_id, day_of_the_week, time):
    teacher = data_provider.get_teacher(teacher_id)
    week = data_provider.whole_week()
    form = BookingForm()
    return render_template('booking.html', teacher=teacher, day_of_the_week=day_of_the_week, time=time, week=week,
                           form=form)


@app.route('/booking_done/', methods=["GET", "POST"])
def render_booking_done():
    form = BookingForm()
    name = form.clientName.data
    weekdays = data_provider.whole_week()
    weekday = weekdays[form.clientWeekday.data]
    time = form.clientTime.data
    phone = form.clientPhone.data
    booking = Booking(weekday, time, name, phone)
    data_provider.save_booking(booking)
    return render_template('booking_done.html', name=name, weekday=weekday, time=time, phone=phone)


if __name__ == '__main__':
    app.run()