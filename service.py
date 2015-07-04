"""
Service for Magic the Gathering Data
"""
import json
from flask import Flask, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from configparser import ConfigParser
import tabledefs

# ATTENTION: AllSets-x.json is a file resource that needs to be downloaded.
# Find it here: http://mtgjson.com/
json_data = json.load(open("AllSets-x.json", "rt", encoding="utf-8"))

app = Flask(__name__)

parser = ConfigParser()
parser.read("creds.ini")
user = parser.get("mysql", "user")
pw = parser.get("mysql", "pw")
db = parser.get("mysql", "db")
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{}:{}@localhost/{}?charset=utf8".format(user, pw, db)
db = SQLAlchemy(app)


def __runquery(query):
    conn = db.get_engine(app).connect()
    res = conn.execute(query)
    return res


card_set_table, card_table, strength_table, mana_table, color_table, text_table, loyalty_table, user_table, deck_table, card_deck_table = tabledefs.get_tables(db)


@app.route("/card/<card_id>")
def get_card(card_id):
    query = db.select([card_table]).where(card_table.c.id == card_id)
    data_set = __runquery(query).fetchall()
    return_result = {}
    if len(data_set) == 1:
        id, artist, type, name, imageName, rarity, layout, set_code = data_set[0]
        card = dict(id=id, artist=artist, type=type, name=name, imageName=imageName, rarity=rarity, layout=layout, set_code=set_code)
        return_result["result"] = card
    else:
        return_result["error"] = "card not found"

    return jsonify(return_result)


@app.route("/strength")
def search_strength():
    power = request.get_json().get("power")
    toughness = request.get_json().get("toughness")
    clause_list = list()
    clause_list.append(strength_table.c.power == power)

    query = db.select([strength_table])
    if power:
        query = query.where(strength_table.c.power == power)
    if toughness:
        query = query.where(strength_table.c.toughness == toughness)

    data = list(__runquery(query).fetchall())
    data_set = [dict(id=id, power=power, toughness=toughness) for id, power, toughness in data]
    return jsonify({"results":data_set})


@app.route("/setinfo/<s_code>")
def get_set_info(s_code):
    query = db.select([card_set_table])
    query = query.where(card_set_table.c.code == s_code)
    res = __runquery(query).fetchone()
    code, name, border, releaseDate, type = res
    set_info =  dict(code=code, name=name, border=border,
                     releaseDate=releaseDate, type=type)

    return jsonify({"results":set_info})


@app.route("/loyalty/<loyalty_num>")
def get_loyalty_info(loyalty_num):
    query = db.select([loyalty_table])
    query = query.where(loyalty_table.c.loyalty == loyalty_num)
    res = __runquery(query)
    res = res.fetchall()
    final_list = [dict(card_id=card_id, loyalty=loyalty)
                  for card_id, loyalty in res]
    return jsonify({"results":final_list})


@app.route("/color")
def get_color_info():
    json_data = request.get_json()
    color_arg = json_data.get("color")
    query = db.select([color_table])
    query = query.where(color_table.c.color_name == color_arg)
    res = __runquery(query)
    res = res.fetchall()
    final_list = [dict(color_name=color_name, card_id=card_id)
                  for rec_id, color_name, card_id in res]
    return jsonify({"results":final_list})

@app.route("/text")
def get_text_info():
    json_data = request.get_json()
    text_arg = json_data.get("text")
    query = db.select([text_table])
    query = query.where(text_table.c.text.like("%{}%".format(text_arg)))
    print(query)
    res = __runquery(query)
    res = res.fetchall()
    final_list = [dict(card_id=card_id, text=text)
                  for card_id, text in res]
    return jsonify({"results":final_list})


@app.route("/adduser", methods=["POST"])
def add_user():
    json_data = request.get_json()
    user_name = json_data.get("user_name")
    query = user_table.insert().values(id=user_name)
    __runquery(query)
    return jsonify({"message":"add user query completed for user: {}".format(user_name)})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
