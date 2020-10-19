import json

import data

teachers = data.teachers

with open("teachers.json", "w") as f:
    json.dump(teachers, f,
              ensure_ascii=False,
              sort_keys=True,
              indent=4,
              separators=(',', ': ')
              )

# with open("teachers.json", "r") as f:
#     contents = f.read()
# teachers = json.loads(contents)

with open("goals.json", "w") as f:
    json.dump(data.goals, f,
              ensure_ascii=False,
              sort_keys=True,
              indent=4,
              separators=(',', ': ')
              )
