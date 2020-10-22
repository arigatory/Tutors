import datetime
import json

import data_provider
from app import db, Teacher, FreeTimes, Goal

# with open("teachers.json", "w") as f:
#     json.dump(teachers, f,
#               ensure_ascii=False,
#               sort_keys=True,
#               indent=4,
#               separators=(',', ': ')
#               )


def load_goals_from_json_to_db():
    with open("goals.json", "r", encoding='utf8') as f:
        goals = json.load(f)
    for k, v in goals.items():
        goal = Goal(rus=v, short=k)
        db.session.add(goal)
    db.session.commit()


def load_teachers_from_json_to_db():
    with open("teachers.json", "r", encoding='utf8') as f:
        teachers = json.load(f)
        for teacher in teachers:
            new_teacher = Teacher(name=teacher['name'],
                                  picture=teacher['picture'],
                                  price=int(teacher['price']),
                                  about=str(teacher['about']),
                                  rating=float(teacher['rating']))
            db.session.add(new_teacher)
            goals = teacher['goals']
            for k in goals:
                goal = db.session.query(Goal).filter(Goal.short == k).first()
                if goal:
                    new_teacher.goals.append(goal)
            free_times = teacher['free']
            whole_week = data_provider.whole_week()
            for weekday_key, weekday_value in whole_week.items():
                for k, v in free_times[weekday_key].items():
                    if v:
                        h = int(k.split(':')[0])
                        t = datetime.time(h, 00)
                        db.session.add(FreeTimes(teacher=new_teacher,
                                                 weekday=weekday_key,
                                                 time=t))
        db.session.commit()

# load_teachers_from_json_to_db()

# load_goals_from_json_to_db()
