from pyscript import window 
from common import csv_to_json
from pyweb import pydom

current_link = window.location.href
exercise_id = current_link.split("?")[1].split("=")[1]

data = csv_to_json("exercises.csv", exercise_id=exercise_id)

pydom["#exercise-name"][0]._js.textContent = data["name"]
