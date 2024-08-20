from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

if TYPE_CHECKING:
    import aiohttp

from .settings import settings

logger = logging.getLogger(__name__)


async def get_moxfield_card(http_session: aiohttp.ClientSession, name: str) -> dict | None:
    logger.debug(f'Fetching card: {name}')
    headers = {
        'content-type': 'application/json',
        'referrer-policy': 'strict-origin-when-cross-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    response = await http_session.get(
        urljoin('/', 'v2/cards/search'), params=dict(q=f'({name}) include:extras'), headers=headers
    )
    if response.ok:
        response_json = await response.json()
        if 'data' not in response_json:
            logger.warning(f'Could not fetch {name} at {response.url}')
            return None
        cards = response_json['data']
        if len(cards) > 1:
            format_legal_cards = filter(lambda c: c['legalities'][settings.target_format.value] == 'legal', cards)
            if not format_legal_cards:
                card = cards[0]
            else:
                relevant_type_cards = filter(lambda c: c['type_line'] not in ['Stickers'], format_legal_cards)
                if not relevant_type_cards:
                    card = list(format_legal_cards)[0]
                else:
                    card = list(relevant_type_cards)[0]
        else:
            card = cards[0]
        logger.info(f'Retrieved {card['id']} for {name}')
        return card
    else:
        logger.warn(f'Bad response status from {response.url}: {response.status}')
        return None


async def list_moxfield_decks(http_session: aiohttp.ClientSession, card_id: str) -> dict[str, Any] | None:
    logger.debug(f'Finding decks for card ID {card_id}')
    headers = {
        'content-type': 'application/json',
        'referrer-policy': 'strict-origin-when-cross-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    response = await http_session.get(
        urljoin('/', 'v2/decks/search-sfw'),
        params=dict(cardID=f'{card_id}', fmt=settings.target_format.value, board='mainboard'),
        headers=headers,
    )
    if response.ok:
        response_json = await response.json()
        if 'totalResults' not in response_json:
            logger.warning(f'Could not find {card_id} at {response.url}')
        logger.info(f'Found {response_json['totalResults']} decks for card ID {card_id}')
        return response_json
    else:
        logger.warn(f'Bad response status from {response.url}: {response.status}')
        return None
