import datetime
import io
import uuid
from dataclasses import dataclass

from PIL import Image
from fpdf import FPDF
from js import Uint8Array, File, URL, document, localStorage
from pyodide.ffi.wrappers import add_event_listener
from pyscript import document, window, display
from pyweb import pydom

from common import copyright, current_version
from common import csv_to_json


@dataclass
class Exercise:
    id: int
    internal_id: str
    name: str
    sets: int
    reps: str


ls_workout_key = "workout"
current_workout = eval(
    localStorage.getItem(ls_workout_key)
    if localStorage.getItem(ls_workout_key)
    else "[]"
)

workout: list[Exercise] = current_workout


def create_pdf():
    class PDF(FPDF):
        def header(self):
            self.set_font("times", "B", 16)
            self.cell(0, 10, "Workout Plan", new_x="LMARGIN", new_y="NEXT", align="C")
            self.ln(5)

        def footer(self):
            self.set_y(-20)
            self.set_font("times", "I", 10)
            self.set_draw_color(180, 180, 180)
            self.set_line_width(0.3)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(2)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

        def add_watermark(self, image_path):
            x, y = self.get_x(), self.get_y()
            page_w = self.w
            page_h = self.h

            with Image.open(image_path) as img:
                img_w, img_h = img.size

            scale = min(page_w / img_w, page_h / img_h)
            new_w = img_w * scale
            new_h = img_h * scale

            x_img = (page_w - new_w) / 2
            y_img = (page_h - new_h) / 2

            self.image(image_path, x=x_img, y=y_img, w=new_w, h=new_h)
            self.set_xy(x, y)

    pdf = PDF()
    pdf.add_page()
    pdf.add_watermark("logo-for-pdf.png")

    pdf.set_font("times", style="", size=14)

    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    pdf.cell(0, 10, current_date, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    exercises = localStorage.getItem(ls_workout_key)
    if exercises:
        exercises = eval(exercises)
        table_width = 90 + 20 + 20 + 40
        page_width = pdf.w - 2 * pdf.l_margin
        x_start = (page_width - table_width) / 2 + pdf.l_margin
        pdf.set_x(x_start)

        row_height = 12

        pdf.set_fill_color(220, 220, 220)
        pdf.cell(90, row_height, "Exercise", border=1, fill=True, align="C")
        pdf.cell(20, row_height, "Sets", border=1, fill=True, align="C")
        pdf.cell(20, row_height, "Reps", border=1, fill=True, align="C")
        pdf.cell(40, row_height, "Weight", border=1, fill=True, align="C")
        pdf.ln()
        for exercise in exercises:
            pdf.set_x(x_start)
            pdf.cell(90, row_height, str(exercise.name), border=1, align="L")
            pdf.cell(20, row_height, str(exercise.sets), border=1, align="C")
            pdf.cell(20, row_height, exercise.reps, border=1, align="C")
            try:
                sets = int(exercise.sets)
            except Exception:
                sets = 1
            placeholders = " | ".join(["____"] * sets)
            pdf.cell(40, row_height, placeholders, border=1, align="C")
            pdf.ln(row_height)

    return pdf


def download_file(*args):
    pdf = create_pdf()
    encoded_data = pdf.output()
    my_stream = io.BytesIO(encoded_data)

    js_array = Uint8Array.new(len(encoded_data))
    js_array.assign(my_stream.getbuffer())

    file = File.new([js_array], "unused_file_name.pdf", {type: "application/pdf"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute(
        "download",
        f"workout_{datetime.datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf",
    )
    hidden_link.setAttribute("href", url)
    hidden_link.click()


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
    info_box.innerHTML = info_content

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
    exercise_id = event.target.parentElement.parentElement.parentElement.getAttribute(
        "data-exercise-id"
    )
    window.open(f"detail.html?exercise_id={exercise_id}", "_blank")


def render_workout(workout: list[Exercise], data, w_item_template):
    w_list = pydom["#workout-list"][0]
    while w_list._js.firstChild:
        w_list._js.removeChild(w_list._js.firstChild)

    for exercise in workout:
        w_item = w_item_template.clone()
        w_item._js.removeAttribute("id")
        w_item.find("#workout-item-name")[0]._js.innerHTML = (
            f"{exercise.name} "
            f'<span style="font-size:0.8em; color:#888;">'
            f"({exercise.sets} of {exercise.reps})"
            f"</span>"
        )
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
    overlay.style.justifyContent = "space-between"
    overlay.style.color = "white"
    overlay.style.fontSize = "1.2rem"
    overlay.style.zIndex = "10"
    overlay.style.gap = "0"
    overlay.style.padding = "32px 0 24px 0"

    inputs_container = document.createElement("div")
    inputs_container.style.display = "flex"
    inputs_container.style.flexDirection = "column"
    inputs_container.style.alignItems = "flex-start"
    inputs_container.style.gap = "10px"
    inputs_container.style.width = "100%"
    inputs_container.style.marginTop = "0"

    label_sets = document.createElement("label")
    label_sets.textContent = "Sets:"
    label_sets.style.marginLeft = "16px"
    label_sets.style.fontSize = "0.95rem"
    label_sets.style.fontWeight = "400"
    label_sets.style.color = "#fff"
    label_sets.style.letterSpacing = "0.01em"
    input_sets = document.createElement("input")
    input_sets.type = "number"
    input_sets.min = "1"
    input_sets.value = "3"
    input_sets.style.marginLeft = "8px"
    input_sets.style.width = "60px"
    label_sets.appendChild(input_sets)

    label_reps = document.createElement("label")
    label_reps.textContent = "Reps per set (comma separated):"
    label_reps.style.marginLeft = "16px"
    label_reps.style.fontSize = "0.95rem"
    label_reps.style.fontWeight = "400"
    label_reps.style.color = "#fff"
    label_reps.style.letterSpacing = "0.01em"
    input_reps = document.createElement("input")
    input_reps.type = "text"
    input_reps.value = "10,10,10"
    input_reps.style.marginLeft = "8px"
    input_reps.style.width = "120px"
    label_reps.appendChild(input_reps)

    inputs_container.appendChild(label_sets)
    inputs_container.appendChild(label_reps)

    buttons_container = document.createElement("div")
    buttons_container.style.display = "flex"
    buttons_container.style.flexDirection = "row"
    buttons_container.style.justifyContent = "center"
    buttons_container.style.alignItems = "center"
    buttons_container.style.gap = "16px"
    buttons_container.style.width = "100%"
    buttons_container.style.marginBottom = "0"

    confirm_btn = document.createElement("button")
    confirm_btn.textContent = "Add"
    confirm_btn.classList.add("btn", "btn-outline-gold", "btn-sm")
    confirm_btn.style.padding = "6px 16px"
    confirm_btn.style.borderRadius = "4px"

    close_btn = document.createElement("button")
    close_btn.textContent = "Cancel"
    close_btn.classList.add("btn", "btn-outline-secondary", "btn-sm")
    close_btn.style.padding = "6px 16px"
    close_btn.style.borderRadius = "4px"
    close_btn.onclick = lambda evt: overlay.remove()

    buttons_container.appendChild(confirm_btn)
    buttons_container.appendChild(close_btn)

    overlay.appendChild(inputs_container)
    overlay.appendChild(document.createElement("div"))
    overlay.appendChild(buttons_container)

    ex_card._js.style.position = "relative"
    ex_card._js.appendChild(overlay)

    def on_confirm_click(evt):
        sets_val = input_sets.value
        reps_val = input_reps.value
        if not sets_val or not reps_val:
            return
        sets = int(sets_val)
        reps = [v for r in reps_val.split(",") if (v := r.strip()) and v.isdigit()]
        if len(reps) != sets:
            return

        ex = Exercise(
            int(exercise_id), str(uuid.uuid4()), exercise_name, sets, reps_val
        )
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
