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

def __json_arg(arg):
    return request.get_json().get(arg)

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
    power = __json_arg("power")
    toughness = __json_arg("toughness")
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
    color_arg = __json_arg("color")
    query = db.select([color_table])
    query = query.where(color_table.c.color_name == color_arg)
    res = __runquery(query)
    res = res.fetchall()
    final_list = [dict(color_name=color_name, card_id=card_id)
                  for rec_id, color_name, card_id in res]
    return jsonify({"results":final_list})

@app.route("/text")
def get_text_info():
    text_arg = __json_arg("text")
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
    user_name = __json_arg("user_name")
    query = user_table.insert().values(id=user_name)
    __runquery(query)
    return jsonify({"message":"add user query completed for user: {}".format(user_name)})


@app.route("/adddeck", methods=["POST"])
def add_deck():
    deck_name = __json_arg("deck_name")
    owner = __json_arg("owner")
    __runquery(deck_table.insert().values(name=deck_name, owner=owner))
    return jsonify({"message":"Deck {} createed under the owner {}".format(deck_name, owner)})


@app.route("/listdecks", methods=["GET"])
def list_decks():
    owner = __json_arg("owner")
    res = __runquery(db.select([deck_table]).where(deck_table.c.owner == owner))
    deck_list = [dict(id=id, name=name, owner=owner) for id, name, owner in res.fetchall()]
    return jsonify({"results":deck_list})

@app.route("/addcard", methods=["POST"])
def add_card():
    deck_id = __json_arg("deck_id")
    card_id = __json_arg("card_id")
    __runquery(card_deck_table.insert().values(deck_id=deck_id, card_id=card_id))
    msg = "Card number: {} added to deck number: {}".format(card_id, deck_id)
    return jsonify({"message":msg})



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
