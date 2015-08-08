from operator import itemgetter
# from service import json_data
from sqlalchemy.sql import select, and_
from sqlalchemy import MetaData, Table, Column, Text, Float, Integer, create_engine, VARCHAR, ForeignKey
from configparser import ConfigParser

def lookup_card_id(conn, card):
    query = select([card_table.c.id]).where(and_(card_table.c.artist == card.get("artist"),
                                                 card_table.c.type == card.get("type"),
                                                 card_table.c.name == card.get("name"),
                                                 card_table.c.imageName == card.get("imageName"),
                                                 card_table.c.rarity == card.get("rarity"),
                                                 card_table.c.layout == card.get("layout"),
                                                 card_table.c.set_code == card.get("set_code")))

    card_rec_id, *_ = conn.execute(query).fetchone()
    return card_rec_id


def populate_set_table(eng):
    conn = eng.connect()
    from service import json_data
    getter = itemgetter(*"code name border releaseDate type".split())
    for key, val in json_data.items():
        code, name, border, releaseDate, type = getter(val)
        conn.execute(card_set_table.insert().values(code=code, name=name, border=border,
                                                    releaseDate=releaseDate, type=type))


def populate_card_table(eng, all_cards):
    conn = eng.connect()
    getter = itemgetter(*"artist type name imageName rarity layout set_code".split())
    for card in all_cards:
        artist, type, name, imageName, rarity, layout, set_code = getter(card)
        query = card_table.insert().values(artist=artist, type=type, name=name,
                                           imageName=imageName, rarity=rarity,
                                           layout=layout, set_code=set_code)
        conn.execute(query)


def populate_strength_table(eng):

    conn = eng.connect()

    for card in cards_by_attr("power"):
        card_rec_id = lookup_card_id(conn, card)
        power, toughness = itemgetter(*"power toughness".split())(card)
        conn.execute(strength_table.insert().values(id=card_rec_id, power=power, toughness=toughness))


def populate_text_table(eng):
    conn = eng.connect()
    for card in cards_by_attr("text"):
        card_id = lookup_card_id(conn, card)
        conn.execute(text_table.insert().values(id=card_id, text=card.get("text")))


def populate_loyalty_table(eng):
    conn = eng.connect()

    for card in cards_by_attr("loyalty"):
        card_id = lookup_card_id(conn, card)
        conn.execute(loyalty_table.insert().values(id=card_id, loyalty=card.get("loyalty")))


def populate_mana_table(eng):
    conn = eng.connect()

    for card in cards_by_attr("cmc"):
        manaCost, cmc = card.get("manaCost"), card.get("cmc")
        card_id = lookup_card_id(conn, card)
        conn.execute(mana_table.insert().values(id=card_id, manaCost=manaCost, cmc=cmc))


def populate_color_table(eng):
    conn = eng.connect()

    for card in cards_by_attr("colors"):
        card_id = lookup_card_id(conn, card)
        for color in card.get("colors"):
            conn.execute(color_table.insert().values(color_name=color, card_id=card_id))


if __name__ == '__main__':
    parser = ConfigParser()
    parser.read("/vagrant/creds.ini")
    user_name  = parser.get("mysql", "user")
    password = parser.get("mysql", "pw")
    db_name = parser.get("mysql", "db")
    url_template = "mysql+pymysql://{}:{}@localhost/{}?charset=utf8"
    url = url_template.format(user_name, password, db_name)
    meta = MetaData()
    card_set_table = Table("card_set", meta,
                           Column("code", VARCHAR(10), primary_key=True),
                           Column("name", Text),
                           Column("border", Text),
                           Column("releaseDate", Text),
                           Column("type", Text))

    card_table = Table("card", meta,
                       Column("id", Integer, autoincrement=True, primary_key=True),
                       Column("artist", Text),
                       Column("type", Text),
                       Column("name", Text),
                       Column("imageName", Text),
                       Column("rarity", Text),
                       Column("layout", Text),
                       Column("set_code", VARCHAR(10), ForeignKey("card_set.code")))

    strength_table = Table("strength", meta,
                           Column("id", Integer, ForeignKey("card.id"), primary_key=True),
                           Column("power", Text),
                           Column("toughness", Text))

    mana_table = Table("mana", meta,
                       Column("id", Integer, ForeignKey("card.id"), primary_key=True),
                       Column("manaCost", Text),
                       Column("cmc", Float))

    color_table = Table("color", meta,
                        Column("id", Integer, autoincrement=True, primary_key=True),
                        Column("color_name", Text),
                        Column("card_id", Integer, ForeignKey("card.id")))

    text_table = Table("text", meta,
                       Column("id", Integer, ForeignKey("card.id"), primary_key=True),
                       Column("text", Text))

    loyalty_table = Table("loyalty", meta,
                          Column("id", Integer, ForeignKey("card.id"), primary_key=True),
                          Column("loyalty", Integer))


    def generate_abridged_set():
        from service import json_data
        getter = itemgetter(*"artist type name imageName rarity layout".split())
        for set_code, v in json_data.items():
            for card in v.get("cards"):
                artist, type, name, imageName, rarity, layout = getter(card)
                new_card = {"artist": artist, "type": type, "name": name,
                            "imageName": imageName, "rarity": rarity, "layout": layout,
                            "set_code": set_code}
                yield new_card

    def generate_abridged_index_set(eng):
        new_card_set = []
        db_recs = eng.connect().execute(select([card_table])).fetchall()
        for id, artist, type, name, imageName, rarity, layout, set_code in db_recs:
            new_card = {"id": id, "artist": artist, "type": type,
                        "name": name, "imageName": imageName, "rarity": rarity,
                        "layout": layout, "set_code": set_code}
            new_card_set.append(new_card)
        return new_card_set

    def cards_by_attr(attr_name):
        from service import json_data
        for set_code, card_set in json_data.items():
            for card in card_set.get("cards"):
                if attr_name in card:
                    card["set_code"] = set_code
                    yield card

    eng = create_engine(url)
    meta.create_all(eng)
    conn = eng.connect()
    populate_set_table(eng)
    print("finished populating set table")
    populate_card_table(eng, generate_abridged_set())
    print("finished populating card table")
    populate_strength_table(eng)
    print("finished populating strength table")
    populate_color_table(eng)
    print("finished populating color table")
    populate_mana_table(eng)
    print("finished populating mana table")
    populate_loyalty_table(eng)
    print("finished populating loyalty table")
    populate_text_table(eng)
    print("finished populating text table")