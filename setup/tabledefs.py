def get_tables(db):
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

    text_table = db.Table("text",
                       db.Column("id", db.Integer, db.ForeignKey("card.id"), primary_key=True),
                       db.Column("text", db.Text))

    loyalty_table = db.Table("loyalty",
                          db.Column("id", db.Integer, db.ForeignKey("card.id"), primary_key=True),
                          db.Column("loyalty", db.Integer))

    deck_table = db.Table("deck",
                      db.Column("id", db.Integer, primary_key=True, autoincrement=True),
                      db.Column("name", db.Text),
                      db.Column("owner", db.VARCHAR(50), db.ForeignKey("user.id")))

    user_table = db.Table("user",
                          db.Column("id", db.VARCHAR(50), primary_key=True))

    card_deck_table = db.Table("card_deck",
                               db.Column("id", db.Integer, primary_key=True),
                               db.Column("deck_id", db.Integer, db.ForeignKey("deck.id")),
                               db.Column("card_id", db.Integer, db.ForeignKey("card.id")))

    return card_set_table, card_table, strength_table, mana_table, color_table, text_table, loyalty_table