import asyncio
import csv
import logging
import os
import pprint

import click
from peewee import chunked

from .jobs import load_moxfield_data
from .models import Card, db
from .settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('__name__')


@click.group()
def cli():
    pass


@cli.command()
@click.option('--filename', '-f', default=settings.collection_file, help='Input collection file')
@click.option(
    '--overwrite/--no-overwrite',
    '-o/-n',
    type=bool,
    default=True,
    help='Overwrite existing records; otherwise, ignores already-imported cards',
)
def load_collection(filename, overwrite):
    logger.info('Loading collection from file')
    db.create_tables([Card], safe=True)
    if overwrite:
        Card.truncate_table()
    try:
        with open(os.path.join(os.getcwd(), filename)) as collection_file:
            reader = csv.DictReader(collection_file)
            cards_args = [
                dict(
                    name=line['Name'],
                    set_code=line['Set code'],
                    set_name=line['Set name'],
                    collector_number=line['Collector number'],
                    foil=line['Foil'],
                    rarity=line['Rarity'],
                    quantity=line['Quantity'],
                )
                for line in reader
            ]
    except FileNotFoundError:
        logger.error('Collection file not found', exc_info=True)
        return
    with db.atomic():
        for batch in chunked(cards_args):
            Card.insert_many(batch).execute().on_conflict_ignore()


@cli.command()
def populate_moxfield():
    logger.info('Populating card records with Moxfield data')
    asyncio.run(load_moxfield_data())


@cli.command()
@click.option(
    '--price',
    '-p',
    default=0.5,
    type=float,
    help='Price threshold to be considered not chaff regardless of number of decks',
)
@click.option(
    '--count',
    '-c',
    default=50,
    type=int,
    help='Number of public decks a card should be in to be considered not chaff',
)
@click.option('--output', '-o', default=False, is_flag=True, help=f'Save output to {settings.output_file}')
def find_chaff(price, count, output):
    cards = (
        Card.select()
        .where(
            (Card.price != 0)
            & (Card.price < price)
            & (Card.moxfield_deck_count < count)
            # Ignore special card types
            & (Card.type_line.not_in(['Stickers', 'Phenomenon']))
            & ~(Card.type_line.startswith('Plane'))
        )
        .order_by(Card.moxfield_deck_count)
    )
    if not cards:
        logger.info('No chaff cards found!')
        return
    card_dicts = [
        dict(
            name=card.name,
            color_identity=card.color_identity,
            type_line=card.type_line,
            set_code=card.set_code,
            quantity=card.quantity,
            price=card.price,
            moxfield_deck_count=card.moxfield_deck_count,
            edhrec_rank=card.edhrec_rank,
            moxfield_decks_url=card.moxfield_decks_url,
        )
        for card in cards
    ]
    if output:
        with open(settings.output_file, 'w') as file:
            fieldnames = [
                'name',
                'color_identity',
                'type_line',
                'set_code',
                'quantity',
                'price',
                'moxfield_deck_count',
                'edhrec_rank',
                'moxfield_decks_url',
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for card in card_dicts:
                writer.writerow(card)
    for card in card_dicts:
        pprint.pprint(card)


if __name__ == '__main__':
    cli()
