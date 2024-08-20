import asyncio
import logging

import aiohttp
from peewee import chunked

from .api import get_moxfield_card, list_moxfield_decks
from .models import Card, db
from .utils import AsyncThrottler

logger = logging.getLogger(__name__)


async def load_moxfield_data() -> None:
    logger.info('Downloading card data from Moxfield')
    try:
        throttler = AsyncThrottler(limit=10, interval=1)
        async with aiohttp.ClientSession('https://api2.moxfield.com/') as http_session:
            for batch in chunked(Card.select().where(Card.type_line == 'Stickers'), 50):
                for card in batch:
                    async with throttler:
                        moxfield_card = await get_moxfield_card(http_session=http_session, name=card.name)
                        if moxfield_card is None:
                            logger.warning('No moxfield card found')
                            continue
                        card.color_identity = moxfield_card['color_identity']
                        card.type_line = moxfield_card['type_line']
                        card.moxfield_id = moxfield_card['id']
                        if 'edhrec_rank' in moxfield_card:
                            card.edhrec_rank = moxfield_card['edhrec_rank']
                        prices = moxfield_card['prices']
                        if 'usd' in prices:
                            card.price = prices['usd']
                        elif 'ck_buy' in prices:
                            card.price = prices['ck_buy']
                        elif 'ct' in prices:
                            card.price = prices['ct']
                        elif 'usd_foil' in prices:
                            card.price = prices['usd_foil']
                        elif 'ck_foil' in prices:
                            card.price = prices['ck_buy']
                        elif 'ct_foil' in prices:
                            card.price = prices['ct']
                        elif 'ck' in prices:
                            card.price = prices['ck']
                        else:
                            logger.info('No pricing data found')
                            card.price = 0
                        moxfield_decks = await list_moxfield_decks(
                            http_session=http_session, card_id=moxfield_card['id']
                        )
                        if moxfield_decks is None:
                            logger.warning('No moxfield decks found')
                            continue
                        card.moxfield_deck_count = moxfield_decks['totalResults']
                with db.atomic():
                    logger.info('Saving batch to database')
                    Card.bulk_update(
                        batch,
                        fields=[
                            'color_identity',
                            'type_line',
                            'moxfield_id',
                            'edhrec_rank',
                            'moxfield_deck_count',
                            'prices',
                            'price',
                        ],
                    )
    except asyncio.CancelledError:
        logger.info('Worker loop closed; exiting job', exc_info=True)
