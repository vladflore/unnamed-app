from common import csv_to_json
from pyscript import document, window, display

from pyweb import pydom
from common import copyright, current_version

from js import Uint8Array, File, URL, document, localStorage
import io
from pyodide.ffi.wrappers import add_event_listener
from fpdf import FPDF
import datetime
import uuid
from dataclasses import dataclass


@dataclass
class Exercise:
    id: int
    internal_id: str
    name: str
    sets: int
    reps: int


ls_workout_key = "workout"
current_workout = eval(
    localStorage.getItem(ls_workout_key)
    if localStorage.getItem(ls_workout_key)
    else "[]"
)


workout: list[Exercise] = current_workout


def download_file(*args):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", style="B", size=16)

    exercises = localStorage.getItem(ls_workout_key)
    if exercises:
        # TODO render the exercises in the PDF
        pdf.cell(40, 10, exercises)

    encoded_data = pdf.output()
    my_stream = io.BytesIO(encoded_data)

    js_array = Uint8Array.new(len(encoded_data))
    js_array.assign(my_stream.getbuffer())

    file = File.new([js_array], "unused_file_name.pdf", {type: "application/pdf"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute(
        "download",
        f"workout_{datetime.datetime.now().strftime('%d.%m.%Y_%H:%M:%S')}.pdf",
    )
    hidden_link.setAttribute("href", url)
    hidden_link.click()
    localStorage.removeItem(ls_workout_key)


def q(selector, root=document):
    return root.querySelector(selector)


w_item_template = pydom.Element(
    q("#workout-item-template").content.querySelector("#workout-item")  # li element
)


def show_info(event):
    info_box = document.createElement("div")
    info_box.style.position = "fixed"
    info_box.style.top = "50%"
    info_box.style.left = "50%"
    info_box.style.width = "80%"
    info_box.style.maxWidth = "600px"
    info_box.style.height = "auto"
    info_box.style.maxHeight = "80%"
    info_box.style.transform = "translate(-50%, -50%)"
    info_box.style.backgroundColor = "rgba(0, 0, 0, 0.9)"
    info_box.style.color = "white"
    info_box.style.padding = "20px"
    info_box.style.borderRadius = "10px"
    info_box.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)"
    info_box.style.overflowY = "auto"
    info_box.style.zIndex = "1000"

    with open("info.txt", "r") as info_file:
        info_content = info_file.read()
    info_box.innerHTML = f"<div>{info_content}</div>"

    close_button = document.createElement("button")
    close_button.textContent = "Close"
    close_button.style.marginTop = "20px"
    close_button.style.padding = "10px 20px"
    close_button.classList.add("btn", "btn-outline-gold", "btn-sm")
    close_button.style.cursor = "pointer"
    close_button.onclick = lambda event: info_box.remove()

    info_box.appendChild(close_button)
    document.body.appendChild(info_box)


def open_exercise(event):
    exercise_id = event.target.parentElement.parentElement.parentElement.id
    window.open(f"detail.html?exercise_id={exercise_id}", "_blank")


def render_workout(workout: list[Exercise], data, w_item_template):
    w_list = pydom["#workout-list"][0]
    while w_list._js.firstChild:
        w_list._js.removeChild(w_list._js.firstChild)

    for exercise in workout:
        w_item = w_item_template.clone()
        w_item._js.removeAttribute("id")
        w_item.find("#workout-item-name")[
            0
        ]._js.textContent = f"{exercise.name} - {exercise.sets}x{exercise.reps}"
        w_item.find("#workout-item-remove")[
            0
        ]._js.onclick = remove_exercise_from_workout
        w_item.find("#workout-item-remove")[0]._js.setAttribute(
            "data-exercise-id", exercise.id
        )
        w_item.find("#workout-item-remove")[0]._js.setAttribute(
            "data-workout-exercise-id", exercise.internal_id
        )
        w_list.append(w_item)


def add_exercise_to_workout(event):
    exercise_id = event.target.parentElement.parentElement.parentElement.parentElement.getAttribute(
        "data-exercise-id"
    )
    exercise_name = event.target.parentElement.parentElement.parentElement.parentElement.getAttribute(
        "data-exercise-name"
    )
    add_sets_and_reps(exercise_id, exercise_name)


def add_sets_and_reps(exercise_id, exercise_name):
    ex_card = pydom["#ex-" + exercise_id][0]

    overlay = document.createElement("div")
    overlay.style.position = "absolute"
    overlay.style.top = "0"
    overlay.style.left = "0"
    overlay.style.width = "100%"
    overlay.style.height = "100%"
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.8)"
    overlay.style.display = "flex"
    overlay.style.flexDirection = "column"
    overlay.style.alignItems = "center"
    overlay.style.justifyContent = "center"
    overlay.style.color = "white"
    overlay.style.fontSize = "1.2rem"
    overlay.style.zIndex = "10"
    overlay.style.gap = "10px"
    overlay.textContent = ""

    label_sets = document.createElement("label")
    label_sets.textContent = "Sets:"
    input_sets = document.createElement("input")
    input_sets.type = "number"
    input_sets.min = "1"
    input_sets.value = "3"
    input_sets.style.marginLeft = "8px"
    input_sets.style.width = "60px"
    label_sets.appendChild(input_sets)

    label_reps = document.createElement("label")
    label_reps.textContent = "Reps per set:"
    input_reps = document.createElement("input")
    input_reps.type = "number"
    input_reps.min = "1"
    input_reps.value = "10"
    input_reps.style.marginLeft = "8px"
    input_reps.style.width = "60px"
    label_reps.appendChild(input_reps)

    confirm_btn = document.createElement("button")
    confirm_btn.textContent = "Add"
    confirm_btn.classList.add("btn", "btn-outline-gold", "btn-sm")
    confirm_btn.style.marginTop = "10px"
    confirm_btn.style.padding = "6px 16px"
    confirm_btn.style.borderRadius = "4px"

    close_btn = document.createElement("button")
    close_btn.textContent = "Cancel"
    close_btn.classList.add("btn", "btn-outline-secondary", "btn-sm")
    close_btn.style.marginTop = "10px"
    close_btn.style.padding = "6px 16px"
    close_btn.style.borderRadius = "4px"
    close_btn.onclick = lambda evt: overlay.remove()

    overlay.appendChild(label_sets)
    overlay.appendChild(label_reps)
    overlay.appendChild(confirm_btn)
    overlay.appendChild(close_btn)

    ex_card._js.style.position = "relative"
    ex_card._js.appendChild(overlay)

    def on_confirm_click(evt):
        sets_val = input_sets.value
        reps_val = input_reps.value
        if not sets_val or not reps_val:
            return
        sets = int(sets_val)
        reps = int(reps_val)
        ex = Exercise(int(exercise_id), str(uuid.uuid4()), exercise_name, sets, reps)
        workout.append(ex)
        localStorage.setItem(ls_workout_key, workout)
        show_sidebar()
        render_workout(workout, data, w_item_template)
        overlay.remove()

    confirm_btn.onclick = on_confirm_click


def remove_exercise_from_workout(event):
    exercise_id = event.target.getAttribute("data-exercise-id")
    workout_ex_id = event.target.getAttribute("data-workout-exercise-id")
    for i, ex in enumerate(workout):
        if ex.id == int(exercise_id) and ex.internal_id == workout_ex_id:
            del workout[i]
            break
    localStorage.setItem(ls_workout_key, workout)
    w_list = pydom["#workout-list"][0]
    w_list._js.removeChild(event.target.parentElement)
    if len(workout) == 0:
        pydom[workout_sidebar_el_id][0]._js.classList.add("d-none")
        localStorage.removeItem(ls_workout_key)


def clear_workout(event):
    workout.clear()
    localStorage.removeItem(ls_workout_key)
    w_list = pydom["#workout-list"][0]
    while w_list._js.firstChild:
        w_list._js.removeChild(w_list._js.firstChild)
    hide_sidebar()


def create_card_exercise(template, data):
    exercise_html = template.clone()
    exercise_html.id = f"ex-{data['id']}"
    exercise_html._js.setAttribute("data-exercise-name", data["name"])
    exercise_html._js.setAttribute("data-exercise-id", data["id"])

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

    yt_video_link = f"https://www.youtube.com/embed/{data['yt_video_id']}"
    (exercise_html.find("#video-link")[0])._js.href = yt_video_link

    (exercise_html.find("#add-ex-to-workout")[0])._js.onclick = add_exercise_to_workout

    return exercise_html


def filter_library(event):
    str = event.target.parentElement.children[0].value
    # TODO implement filtering
    pydom["#search-input"][0]._js.value = "Need more ☕️ to work :)"


# Identifiers
exercises_row_id = "#exercises-row"
exercise_card_template_id = "#exercise-card-template"
copyright_el_id = "#copyright"
version_el_id = "#version"
footer_el_id = "#footer"
workout_sidebar_el_id = "#workout-sidebar"

download_pdf_btn_id = "download-workout"
clear_workout_btn_id = "clear-workout"


# DOM elements
exercises_row = pydom[exercises_row_id][0]
exercise_template = pydom.Element(
    q(exercise_card_template_id).content.querySelector("#card-exercise")
)

data = csv_to_json("exercises.csv")

for exercise_data in data:
    exercise_html = create_card_exercise(exercise_template, exercise_data)
    exercises_row.append(exercise_html)

copyright_element = pydom[copyright_el_id][0]
copyright_element._js.innerHTML = copyright()

version_element = pydom[version_el_id][0]
version_element._js.textContent = f"Version {current_version()}"

pydom[footer_el_id][0]._js.classList.remove("d-none")

add_event_listener(document.getElementById(download_pdf_btn_id), "click", download_file)


def show_sidebar():
    pydom[workout_sidebar_el_id][0]._js.classList.remove("d-none")


def hide_sidebar():
    pydom[workout_sidebar_el_id][0]._js.classList.add("d-none")


if workout:
    show_sidebar()
    render_workout(workout, data, w_item_template)
else:
    hide_sidebar()
