"""
Service for Magic the Gathering Data
"""
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

card_set_table, card_table, strength_table, mana_table, color_table, text_table, loyalty_table = tabledefs.get_tables(db)


@app.route("/card/<card_id>")
def get_card(card_id):
    query = db.select([card_table]).where(card_table.c.id == card_id)
    data_set = __runquery(query).fetchall()
    return_result = {}
    if len(data_set) == 1:
        id, artist, type, name, image_name, rarity, layout, set_code = data_set[0]
        card = dict(card_id=id, artist=artist, type=type,
                    name=name, imageName=image_name, rarity=rarity,
                    layout=layout, set_code=set_code)

        return_result["results"] = card
    else:
        return_result["error"] = "card not found"

    return jsonify(return_result)


@app.route("/setinfo/<s_code>")
def get_set_info(s_code):
    query = db.select([card_set_table])
    query = query.where(card_set_table.c.code == s_code)
    res = __runquery(query).fetchone()
    code, name, border, release_date, type = res
    set_info = dict(code=code, name=name, border=border,
                    releaseDate=release_date, type=type)

    return jsonify({"results": set_info})


@app.route("/getinfo")
def get_info():
    power = request.args.get("power")
    toughness = request.args.get("toughness")
    color = request.args.get("color")
    loyalty = request.args.get("loyalty")
    text = request.args.get("text")

    # columns to work with
    query = db.select([card_table.c.name, card_table.c.type, card_table.c.rarity,
                       card_table.c.artist, card_set_table.c.name])

    # build the join chain to select from (based on what was passed in.
    join_chain = card_table
    if power or toughness:
        join_chain = join_chain.join(strength_table)
    if color:
        join_chain = join_chain.join(color_table)
    if loyalty:
        join_chain = join_chain.join(loyalty_table)
    if text:
        join_chain = join_chain.join(text_table)

    query = query.select_from(join_chain)

    if power:
        query = query.where(strength_table.c.power == power)
    if toughness:
        query = query.where(strength_table.c.toughness == toughness)
    if color:
        query = query.where(color_table.c.color_name == color)
    if loyalty:
        query = query.where(loyalty_table.c.loyalty == loyalty)
    if text:
        query = query.where(text_table.c.text.like("%" + text + "%"))

    # prevent letting search results use up system memory
    query = query.limit(1000)

    res = __runquery(query)
    res = res.fetchall()
    data_set = [dict(name=name, type=type, rarity=rarity, artist=artist, set_name=set_name)
                for name, type, rarity, artist, set_name in res]
    return jsonify({"results": data_set})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
