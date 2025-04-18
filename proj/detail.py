from pyscript import window, display

current_link = window.location.href
exercise_id = current_link.split("?")[1].split("=")[1]
display(exercise_id)
