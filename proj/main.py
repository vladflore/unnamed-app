from common import csv_to_json
from pyscript import document, window, display
from pyweb import pydom
from common import copyright, current_version


def q(selector, root=document):
    return root.querySelector(selector)


def open_exercise(event):
    # TODO consider using data-* attributes
    card_id = event.target.parentElement.parentElement.parentElement.id
    window.open(f"detail.html?exercise_id={card_id}", "_blank")


def create_card_exercise(template, data):
    exercise_html = template.clone()
    exercise_html.id = data["id"]
    (
        exercise_html.find("#card-img")[0]
    )._js.src = f"./assets/exercises/{data['thumbnail_url']}"
    (exercise_html.find("#card-img")[0])._js.alt = data["name"]

    (exercise_html.find("#card-title")[0])._js.textContent = data["name"]
    (exercise_html.find("#card-title")[0])._js.onclick = open_exercise

    (exercise_html.find("#badge-primary")[0])._js.textContent = data["category"]

    secondary_badges = data["body_parts"].split(",")
    badges_container = exercise_html.find("#badges")[0]
    for i, badge in enumerate(secondary_badges):
        new_badge = (
            exercise_html.find("#badge-secondary")[0].clone()
            if i > 0
            else exercise_html.find("#badge-secondary")[0]
        )
        new_badge._js.textContent = badge
        badges_container._js.append(new_badge._js)

    (exercise_html.find("#video-link")[0])._js.href = data["video_url"]

    return exercise_html

def filter_library(event):
    str = event.target.parentElement.children[0].value
    display(str)

# Identifiers
exercises_row_id = "#exercises-row"
exercise_card_template_id = "#exercise-card-template"

# DOM elements
exercises_row = pydom[exercises_row_id][0]
exercise_template = pydom.Element(
    q(exercise_card_template_id).content.querySelector("#card-exercise")
)

data = csv_to_json("exercises.csv")

for idx, exercise_data in enumerate(data):
    exercise_html = create_card_exercise(exercise_template, exercise_data)
    exercises_row.append(exercise_html)

copyright_element = pydom["#copyright"][0]
copyright_element._js.innerHTML = copyright()

version_element = pydom["#version"][0]
version_element._js.textContent = f"Version: {current_version()}"

pydom["#footer"][0]._js.classList.remove("d-none")