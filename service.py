"""
Service for Magic the Gathering Data
"""
import json
from flask import Flask, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from configparser import ConfigParser

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


def __connect():
    return db.get_engine(app).connect()


card_set_table = db.Table("card_set",
                       db.Column("code", db.VARCHAR(10), primary_key=True),
                       db.Column("name", db.Text),
                       db.Column("border", db.Text),
                       db.Column("releaseDate", db.Text),
                       db.Column("type", db.Text))

card_table = db.Table("card", 
                   db.Column("id", db.Integer, autoincrement=True, primary_key=True),
                   db.Column("artist", db.Text),
                   db.Column("type", db.Text),
                   db.Column("name", db.Text),
                   db.Column("imageName", db.Text),
                   db.Column("rarity", db.Text),
                   db.Column("layout", db.Text),
                   db.Column("set_code", db.VARCHAR(10), db.ForeignKey("card_set.code")))

strength_table = db.Table("strength", 
                       db.Column("id", db.Integer, db.ForeignKey("card.id"), primary_key=True),
                       db.Column("power", db.Text),
                       db.Column("toughness", db.Text))

mana_table = db.Table("mana", 
                   db.Column("id", db.Integer, db.ForeignKey("card.id"), primary_key=True),
                   db.Column("manaCost", db.Text),
                   db.Column("cmc", db.Float))

color_table = db.Table("color", 
                    db.Column("id", db.Integer, autoincrement=True, primary_key=True),
                    db.Column("color_name", db.Text),
                    db.Column("card_id", db.Integer, db.ForeignKey("card.id")))

text_table = db.Table("db.Text", 
                   db.Column("id", db.Integer, db.ForeignKey("card.id"), primary_key=True),
                   db.Column("db.Text", db.Text))

loyalty_table = db.Table("loyalty", 
                      db.Column("id", db.Integer, db.ForeignKey("card.id"), primary_key=True),
                      db.Column("loyalty", db.Integer))

@app.route("/card/<card_id>")
def get_card(card_id):
    conn = __connect()
    query = db.select([card_table]).where(card_table.c.id == card_id)
    data_set = conn.execute(query).fetchall()
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
    conn = __connect()
    power = request.get_json().get("power")
    toughness = request.get_json().get("toughness")
    clause_list = list()
    clause_list.append(strength_table.c.power == power)

    query = db.select([strength_table])
    if power:
        query = query.where(strength_table.c.power == power)
    if toughness:
        query = query.where(strength_table.c.toughness == toughness)

    data = list(conn.execute(query).fetchall())
    data_set = [dict(id=id, power=power, toughness=toughness) for id, power, toughness in data]
    return jsonify({"results":data_set})
    

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

