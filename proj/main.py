from common import csv_to_json
from pyscript import document, window
from pyweb import pydom
from common import copyright, current_version

from js import Uint8Array, File, URL, document, localStorage
import io
from pyodide.ffi.wrappers import add_event_listener
from fpdf import FPDF
import datetime

workout: list[int] = []


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
    # TODO consider using data-* attributes
    exercise_id = event.target.parentElement.parentElement.parentElement.id
    window.open(f"detail.html?exercise_id={exercise_id}", "_blank")


def add_exercise_to_workout(event):
    exercise_id = event.target.parentElement.parentElement.parentElement.parentElement.id
    workout.append(exercise_id)
    localStorage.setItem(ls_workout_key, workout)


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

download_pdf_btn_id = "download"

ls_workout_key = "workout"

# DOM elements
exercises_row = pydom[exercises_row_id][0]
exercise_template = pydom.Element(
    q(exercise_card_template_id).content.querySelector("#card-exercise")
)

data = csv_to_json("exercises.csv")

for idx, exercise_data in enumerate(data):
    exercise_html = create_card_exercise(exercise_template, exercise_data)
    exercises_row.append(exercise_html)

copyright_element = pydom[copyright_el_id][0]
copyright_element._js.innerHTML = copyright()

version_element = pydom[version_el_id][0]
version_element._js.textContent = f"Version {current_version()}"

pydom[footer_el_id][0]._js.classList.remove("d-none")

add_event_listener(document.getElementById(download_pdf_btn_id), "click", download_file)

current_workout = localStorage.getItem(ls_workout_key)
if current_workout:
    pydom[workout_sidebar_el_id][0]._js.classList.remove("d-none")
    # Render the workout
else:
    pydom[workout_sidebar_el_id][0]._js.classList.add("d-none")
