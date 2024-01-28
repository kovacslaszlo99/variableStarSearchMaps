#!/usr/bin/env python3

import json
import os
import shutil
import time
from datetime import datetime
from typing import Dict, List

import requests
import xmltodict
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


def get_saved_stars():
    stars = []
    db = db_read()
    for item in db:
        if not item["name"] in stars:
            stars.append(item["name"])
    stars = sorted(stars)
    return stars


def get_saved_star_maps(star):
    maps = []
    db = db_read()
    for item in db:
        if item["name"] == star:
            maps.append(item)
    return maps


def get_row(image):
    db = db_read()
    for item in db:
        if item["image"] == image:
            return item
    return "-"


def url_get(url: str) -> str:
    r = requests.get(url)
    res = r.text
    return res


def image_urls(json_text: str):
    res = []
    if "Internal Server Error" in json_text:
        return {}
    d = json.loads(json_text)
    if "errors" in d.keys():
        return d
    return d["image_uri"]


def image_dow(url: str, data):
    d = {}
    if not os.path.exists("static/maps"):
        os.mkdir("static/maps")
    name = url.split("/")[-1].split("?")[0]
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open("./static/maps/" + name, "wb") as f:
            shutil.copyfileobj(res.raw, f)
    else:
        d["status"] = False
        d["message"] = "A kép letöltése nem sikerült!"
        return d
    d["status"] = True
    db_append(data[0], name, data[2], data[1], data[3], data[4], data[5])
    return d


def db_read() -> List[Dict[str, str]]:
    try:
        f = open("db.json")
        json_text = f.read()
        f.close()
        db = json.loads(json_text)
        return db
    except FileNotFoundError:
        return []


def db_push(db, d):
    counter = 0
    is_in = False
    for item in db:

        if (
            item["name"] == d["name"]
            and item["maglimit"] == d["maglimit"]
            and item["fov"] == d["fov"]
            and item["resolution"] == d["resolution"]
            and item["north"] == d["north"]
            and item["east"] == d["east"]
        ):
            is_in = True
            break
        counter += 1
    if is_in:
        db[counter] = d
    else:
        db = db + [d]
    return db


def db_append(name, image, maglimit, fov, resolution, north, east):
    now = datetime.now()
    d = {}
    d["name"] = name
    d["image"] = image
    d["maglimit"] = int(maglimit)
    d["fov"] = int(fov)
    d["resolution"] = int(resolution)
    d["north"] = north
    d["east"] = east
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    d["date"] = date_time
    if not os.path.exists("db.json"):
        with open("db.json", "w") as outfile:
            json.dump([d], outfile)
    else:
        old = db_read()
        new = db_push(old, d)
        # old = old + [d]
        with open("db.json", "w") as outfile:
            json.dump(new, outfile)


@app.route("/")
def index():
    stars = get_saved_stars()
    return render_template("index.html", stars=stars)


@app.route("/chart")
def chart():
    star = request.args.get("star")
    filename = "static/chart/" + star.replace(" ", "+") + ".png"
    if os.path.exists(filename):
        return send_file(
            "static/chart/" + star.replace(" ", "+") + ".png", mimetype="image/png"
        )
    else:
        now = datetime.now()
        date_time_now = now.strftime("%Y.%m.%d")
        date_time_old = (now - relativedelta(years=2)).strftime("%Y.%m.%d")
        url = (
            "http://vcssz.mcse.hu/index3.php?display_mode=normal&display_form=1&action=showlc&star="
            + star.replace(" ", "+")
            + "&obsDate_from="
            + date_time_old
            + "&obsDate_to="
            + date_time_now
            + "&obsDate_type=date&obsCode=&time_range_days=10&select_to_jd=0"
        )
        print(url)
        soup = BeautifulSoup(url_get(url))
        imgs = soup.find_all("img")
        myimg = [item for item in imgs if str(item).find("pointer_div") > 0][0]
        image = myimg["src"]
        image_url = "http://vcssz.mcse.hu/" + image
        print(image_url)
        ment_name = star.replace(" ", "+")
        cmd = f"wget {image_url} -O ./static/chart/{ment_name}.png 2> /dev/null"
        print(cmd)
        os.system(cmd)
        # res = requests.get(image_url, stream=True)
        # if res.status_code == 200:
        #    with open("./static/chart/" + ment_name + ".png", "wb") as f:
        #        shutil.copyfileobj(res.raw, f)

        return send_file(
            "./static/chart/" + star.replace(" ", "+") + ".png", mimetype="image/png"
        )


@app.route("/star")
def star_maps():
    name = request.args.get("name")
    maps = get_saved_star_maps(name)
    norm = [item for item in maps if item["east"] == "right" and item["north"] == "up"]
    zenit = [item for item in maps if item["east"] == "left" and item["north"] == "up"]
    newton = [
        item for item in maps if item["east"] == "left" and item["north"] == "down"
    ]
    norm = sorted(norm, key=lambda item: item["fov"], reverse=True)
    zenit = sorted(zenit, key=lambda item: item["fov"], reverse=True)
    newton = sorted(newton, key=lambda item: item["fov"], reverse=True)
    return render_template(
        "star_maps.html", name=name, maps=maps, norm=norm, zenit=zenit, newton=newton
    )


def kisebb(name, north, east, fov, resolution):
    db = db_read()
    maps = [
        item
        for item in db
        if item["name"] == name
        and item["north"] == north
        and item["east"] == east
        and item["resolution"] == resolution
    ]

    rend = sorted(maps, key=lambda item: item["fov"], reverse=True)
    i = 0
    while i < len(rend):
        if rend[i]["fov"] == fov:
            if not i + 1 == len(rend):
                return rend[i + 1]["image"]
            else:
                return None
        i += 1
    return None


def nagyobb(name, north, east, fov, resolution):
    db = db_read()
    maps = [
        item
        for item in db
        if item["name"] == name
        and item["north"] == north
        and item["east"] == east
        and item["resolution"] == resolution
    ]
    rend = sorted(maps, key=lambda item: item["fov"])
    i = 0
    while i < len(rend):
        if rend[i]["fov"] == fov:
            if not i + 1 == len(rend):
                return rend[i + 1]["image"]
            else:
                return None
        i += 1
    return ""


@app.route("/map")
def map():
    image = request.args.get("image")
    row = get_row(image)
    name = row["name"]
    north = row["north"]
    east = row["east"]
    minusz = kisebb(name, north, east, row["fov"], row["resolution"])
    plusz = nagyobb(name, north, east, row["fov"], row["resolution"])
    return render_template(
        "map.html",
        image=image,
        star_name=name,
        north=north,
        east=east,
        plusz=plusz,
        minusz=minusz,
    )


@app.route("/image_dow_p")
def dow_p():
    time.sleep(2)
    return json.dumps({"status": True})


def star_data_reformat(d):
    tmp = d["VOTABLE"]["RESOURCE"]["TABLE"]["DATA"]["TABLEDATA"]["TR"]["TD"]
    data_type = ["auid", "name", "const", "radec2000", "varType", "maxMag", "maxPass", "minMag", "minPass", "epoch", "novaYr", "period", "riseDur", "specType", "disc"]
    out = {data_type[i]: tmp[i] for i in range(15)}
    return out


@app.route("/star_data")
def star_data():
    url = "https://www.aavso.org/vsx/index.php?view=query.votable&ident=Gam+Cas"
    # variablestar_db.json
    d = xmltodict.parse(url_get(url))
    data = star_data_reformat(d)
    return data


@app.route("/image_dow")
def dow():
    name = request.args.get("name")
    maglimit = request.args.get("maglimit", 14.5)
    fov = request.args.get("fov", 60)
    resolution = request.args.get("resolution", 300)
    north = request.args.get("north", "up")
    east = request.args.get("east", "right")
    if not name:
        return json.dumps({"status": False, "message": "Nincs megadav a név!"})
    url = (
        "https://app.aavso.org/vsp/api/chart/?format=json&"
        + "star="
        + name
        + "&fov="
        + str(fov)
        + "&maglimit="
        + str(maglimit)
        + "&resolution="
        + str(resolution)
        + "&north="
        + north
        + "&east="
        + east
    )
    print(url)
    image = image_urls(url_get(url))
    if type(image) == dict:
        return json.dumps({"status": False})
    return json.dumps(image_dow(image, [name, fov, maglimit, resolution, north, east]))


if __name__ == "__main__":
    app.run(debug=True)  # listen on localhost ONLY
    # app.run(debug=True, host='0.0.0.0')    # listen on all public IPs
