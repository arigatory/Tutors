import json
import random


def get_teacher(id):
    with open("teachers.json", "r", encoding='utf8') as f:
        teachers = json.load(f)
    for t in teachers:
        if t['id'] == id:
            return t
    return None


def get_teachers(n=0):
    try:
        with open("teachers.json", "r", encoding='utf8') as f:
            teachers = json.load(f)
            random.shuffle(teachers)
            if n == 0:
                return teachers
            else:
                return teachers[:n]
    except FileNotFoundError:
        return []


def get_goal(key):
    with open("goals.json", "r", encoding='utf8') as f:
        goals = json.load(f)
    for k, v in goals.items():
        if k == key:
            return v
    return None


def whole_week():
    return {
        "mon": "Понедельник",
        "tue": "Вторник",
        "wed": "Среда",
        "thu": "Четверг",
        "fri": "Пятница",
        "sat": "Суббота",
        "sun": "Воскресенье"
    }


def get_goals():
    with open("goals.json", "r", encoding='utf8') as f:
        goals = json.load(f)
        return goals


def save_booking(booking):
    with open("booking.json", "r", encoding='utf8') as f:
        bookings = json.load(f)
        bookings.append(booking.__dict__)

    with open("booking.json", "w", encoding='utf8') as f:
        json.dump(bookings, f,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=4,
                  separators=(',', ': ')
                  )
