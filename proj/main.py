from pyscript import document, window
from pyweb import pydom


def q(selector, root=document):
    return root.querySelector(selector)


def open_exercise(event):
    # TODO consider using data-* attributes
    card_id = event.target.parentElement.parentElement.parentElement.id
    window.open(f"detail.html?exercise_id={card_id}", "_blank")


def create_card_exercise(template, data):
    exercise_html = template.clone()
    exercise_html.id = f"exercise-{data['id']}"
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

    (
        exercise_html.find("#primary")[0]
    )._js.textContent = f"Primary: {data['primary_muscles']}"
    (
        exercise_html.find("#secondary")[0]
    )._js.textContent = f"Secondary: {data['secondary_muscles']}"

    (exercise_html.find("#video-link")[0])._js.href = data["video_url"]

    return exercise_html


# Identifiers
exercises_row_id = "#exercises-row"
exercise_card_template_id = "#exercise-card-template"

# DOM elements
exercises_row = pydom[exercises_row_id][0]
exercise_template = pydom.Element(
    # TODO Check if the `querySelector` is actually working
    q(exercise_card_template_id).content.querySelector(".col-md-4")
)

data = [
    {
        "name": "Body Weight Squat",
        "category": "Strength",
        "body_parts": "Legs",
        "primary_muscles": "Quadriceps",
        "secondary_muscles": "Glutes",
        "thumbnail_url": "body_weight_squat.png",
        "video_url": "https://www.youtube.com/watch?v=l83R5PblSMA&ab_channel=PureGym",
        "execution": "",
        "key_cues": "",
    },
    {
        "name": "Chin-Up",
        "category": "Strength",
        "body_parts": "Arms,Back,Core",
        "primary_muscles": "Latissimus Dorsi,Biceps Brachii,Brachialis,Brachioradialis",
        "secondary_muscles": "Rhomboids,Trapezius,Pectoralis Minor,Deltoids,Core",
        "thumbnail_url": "placeholder.png",
        "video_url": "https://www.youtube.com/watch?v=Dl9vrk_AquU&ab_channel=kenwhittier",
        "execution": "",
        "key_cues": "",
    },
    {
        "name": "Pull-Up",
        "category": "Strength",
        "body_parts": "Arms,Back,Core",
        "primary_muscles": "Latissimus Dorsi,Trapezius,Rhomboids,Teres Major",
        "secondary_muscles": "Biceps Brachii,Brachialis,Brachioradialis,Deltoids,Core",
        "thumbnail_url": "pull_up.png",
        "video_url": "https://www.youtube.com/watch?v=aAggnpPyR6E&ab_channel=CrossFit",
        "execution": "",
        "key_cues": "",
    },
]
for idx, exercise_data in enumerate(data):
    exercise_data["id"] = str(idx + 1)
    exercise_html = create_card_exercise(exercise_template, exercise_data)
    exercises_row.append(exercise_html)
