
# vert => 34
# orange => 202
# rouge => 196

import time
import datetime
import random
import hashlib
import json

def get_hazard_pers(n: int):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")  # Format AAAAMMJJ
    # Créer un seed à partir du hash de la date
    seed = int(hashlib.sha256(date_str.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed)
    index = random.randint(0, n - 1)
    # Retourner l'élément à l'index choisi
    return index

def check_digit(answer: str, index: int):
    end = index
    while end < len(answer) and answer[end].isdigit():
        end += 1
    if index < end:
        substr = answer[index:end]
        try:
            date = int(substr)
        except ValueError:
            date = 0
    else:
        date = 0

    return date

def check_digit(answer: str, index: int):
    end = index
    while end < len(answer) and answer[end].isdigit():
        end += 1
    if index < end:
        substr = answer[index:end]
        try:
            return int(substr)
        except ValueError:
            return 0
    return 0

def compare_date(answer: str):
    if answer == "None":
        return 0
    date = 0
    markers = {
        "VY": 3500,
        "YT": 1500,
        "YS": 590,
        "SA": 3441,
        "TA": 3021,
        "FA": 2500
    }
    for marker, fallback in markers.items():
        if marker in answer:
            index = answer.find(marker) + 3
            date += check_digit(answer, index)
        else:
            date += fallback
    return date

def list_green(guest, answer):
    for i in guest:
        for j in answer:
            if i == j:
                return "green"
    return "red"

def compare_vector(guest, answer, categories: list[str]):
    returne = []
    up = []
    # Comparaison du premier élément
    if guest.name == answer.name:
        returne.append("green")
    else:
        returne.append("red")

    # Comparaison des autres éléments
    for i in categories:
        if i != "id":
            if i in ["birth", "death"]:
                date_guest = compare_date(getattr(guest, i))
                date_answer = compare_date(getattr(answer, i))

                if date_guest == date_answer:
                    returne.append("green")
                elif abs(date_guest - date_answer) < 600:
                    returne.append("orange")
                else:
                    returne.append("red")
                if date_guest < date_answer:
                    up.append("&#129033")  # U+1F809
                elif date_answer < date_guest:
                    up.append("&#129035")  # U+1F807
            else:
                if getattr(guest, i) == getattr(answer, i):
                    returne.append("green")
                else:
                    if isinstance(getattr(guest, i), list) or isinstance(getattr(answer, i), list):
                        ret = list_green(getattr(guest, i), getattr(answer, i))
                        returne.append(ret)
                    else:
                        returne.append("red")
    return returne, up


def init(n: int):
    answer = get_hazard_pers(n)
    return answer

def check_guess(guest_db, answer, categories):
    result = []
    guess_answer = []
    if not guest_db:
        result.append("Guess not found on base")
        guess_answer.append(result)
        return guess_answer

    found = "0"
    color, up = compare_vector(guest_db, answer, categories)

    if color[0] == "green":
        found = "1"
    j = 0
    for i in categories:
        if i != "id":
            if i in ["birth", "death"] and color[j] != "green" and j-2< len(up):
                result.append(f'<span style="color:{color[j]};">{getattr(guest_db, i)} {up[j-2]}</span>')
            else:
                let = ""
                if isinstance(getattr(guest_db, i), list):
                    for i in getattr(guest_db, i):
                        let += i + ", "
                    let = let[:-2]
                else:
                    let = getattr(guest_db, i)
                result.append(f'<span style="color:{color[j]};">{let}</span>')
        j += 1
    result = {
        "columns": result,
        "found": found,
        "color": color
    }
    return result
