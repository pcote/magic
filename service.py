"""
Service for Magic the Gathering Data
"""
import json
from flask import Flask, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from configparser import ConfigParser
import tabledefs



app = Flask(__name__)

parser = ConfigParser()
parser.read("./creds.ini")
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

card_set_table, card_table, strength_table, mana_table, color_table, text_table, loyalty_table  = tabledefs.get_tables(db)


@app.route("/card/<card_id>")
def get_card(card_id):
    query = db.select([card_table]).where(card_table.c.id == card_id)
    data_set = __runquery(query).fetchall()
    return_result = {}
    if len(data_set) == 1:
        id, artist, type, name, imageName, rarity, layout, set_code = data_set[0]
        card = dict(card_id=id, artist=artist, type=type, name=name, imageName=imageName, rarity=rarity, layout=layout, set_code=set_code)
        return_result["results"] = card
    else:
        return_result["error"] = "card not found"

    return jsonify(return_result)


@app.route("/strength")
def search_strength():

    power = request.args.get("power")
    toughness = request.args.get("toughness")

    clause_list = list()
    clause_list.append(strength_table.c.power == power)

    query = db.select([card_table.c.name, card_table.c.type, card_table.c.rarity, card_table.c.artist, card_set_table.c.name])
    query = query.select_from(strength_table.join(card_table.join(card_set_table)))
    if power:
        query = query.where(strength_table.c.power == power)
    if toughness:
        query = query.where(strength_table.c.toughness == toughness)

    data = list(__runquery(query).fetchall())
    data_set = [dict(name=name, type=type, rarity=rarity, artist=artist, set_name=set_name) for name, type, rarity, artist, set_name in data]
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
    color_arg = request.args.get("color")
    color_arg = color_arg.title()
    query = db.select([color_table])
    query = query.where(color_table.c.color_name == color_arg)
    res = __runquery(query)
    res = res.fetchall()
    final_list = [dict(card_id=card_id, color_name=color_name)
                  for rec_id, color_name, card_id in res]
    return jsonify({"results":final_list})

@app.route("/text")
def get_text_info():
    text_arg = request.args.get("text")
    query = db.select([text_table])
    query = query.where(text_table.c.text.like("%{}%".format(text_arg)))
    print(query)
    res = __runquery(query)
    res = res.fetchall()
    final_list = [dict(card_id=card_id, text=text)
                  for card_id, text in res]
    return jsonify({"results":final_list})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
