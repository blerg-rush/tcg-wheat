from urllib.parse import quote_plus

from peewee import BooleanField, CharField, DecimalField, IntegerField, Model
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

from .settings import settings

db = SqliteExtDatabase('collection.db')


class Card(Model):
    name = CharField(index=True)
    color_identity = JSONField(null=True)
    set_code = CharField(max_length=10, index=True)
    set_name = CharField()
    collector_number = CharField(index=True)
    foil = BooleanField(index=True)
    rarity = CharField(index=True)
    quantity = IntegerField(index=True)
    moxfield_deck_count = IntegerField(null=True, index=True)
    prices = JSONField(null=True)
    price = DecimalField(null=True, auto_round=True, decimal_places=2, index=True)
    moxfield_id = CharField(null=True, max_length=10)
    type_line = CharField(null=True, max_length=200)
    edhrec_rank = IntegerField(null=True, index=True)

    class Meta:
        database = db

    @property
    def moxfield_decks_url(self):
        """
        Turn the card's moxfield ID and name into a moxfield decks URL, showing public decks with the card in the mainboard.
        """
        return f'https://www.moxfield.com/decks/public/advanced?format={settings.target_format.value}&sort=updated&cardId={self.moxfield_id}&cardName={quote_plus(self.name)}&board=mainboard'
