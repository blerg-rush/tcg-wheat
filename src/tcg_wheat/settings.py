from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Format(str, Enum):
    BRAWL = 'brawl'
    COMMANDER = 'commander'
    LEGACY = 'legacy'
    MODERN = 'modern'
    OATHBREAKER = 'oathbreaker'
    PAUPER = 'pauper'
    PIONEER = 'pioneer'
    STANDARD = 'standard'


class Settings(BaseSettings):
    collection_file: str = 'input/unsorted.csv'
    output_file: str = 'output/chaff.csv'
    target_format: Format = Format.COMMANDER

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
