# pylint: disable=R0903,W0231
from abc import ABC, abstractmethod
import datetime
import re

import numpy as np
from tqdm import tqdm
from yargy import Parser

from yargy_rules import (
    MEETING_FORM_SENTENCE,
    MEETING_DATE_SENTENCE,
    PAY_DIVIDENDS_SENTENCE,
    DONT_PAY_DIVIDENDS_SENTENCE,
    BOARD_PRESENTED,
    BOARD_SENTENCE,
)

tqdm.pandas()


class BaseRegexRule(ABC):
    @abstractmethod
    def __init__(self):
        self.reg = None
    def __call__(self, text):
        match = self.reg.search(text)
        return None if match is None else match.group(1)


class INNRule(BaseRegexRule):
    def __init__(self):
        self.reg = re.compile(r'ИНН\s(?:эмитента)?[:.]?\s+(\d{10})')


class OGRNRule(BaseRegexRule):
    def __init__(self):
        self.reg = re.compile(r'ОГРН\s(?:эмитента)?[:.]?\s+(\d{13})')


class FullNameRule(BaseRegexRule):
    def __init__(self):
        self.reg = re.compile(
            r'(?:\d\.\d\.?)?\s*Полное\s.+?эмитента\s*(?:\(.+?\))?[:.]?\s*'\
            r'(.+?)\s*(?:\d\.\d\.?)?\s*Сокращенное',
            re.DOTALL
        )


class ShortNameRule(BaseRegexRule):
    def __init__(self):
        self.reg = re.compile(
            r'(?:\d\.\d\.?)?\s*Сокращенное\s.+?эмитента\s*(?:\(.+?\))?[:.]?\s*'\
            r'(.+?)\s*(?:\d\.\d\.?)?\s*Место',
            re.DOTALL
        )


class AddressRule(BaseRegexRule):
    def __init__(self):
        self.reg = re.compile(
            r'(?:\d\.\d\.?)?\s*Место\s.+?эмитента\s*(?:\(.+?\))?[:.]?\s*'\
            r'(.+?)\s*(?:\d\.\d\.?)?\s*ОГРН',
            re.DOTALL
        )


class BaseYargyRule(ABC):
    @abstractmethod
    def __init__(self):
        self.parser = None
    def __call__(self, text):
        match = self.parser.find(text)
        return None if match is None else match.fact.value


class MeetingFormRule(BaseYargyRule):
    def __init__(self):
        self.parser = Parser(MEETING_FORM_SENTENCE)


class MeetingDateRule(BaseYargyRule):
    def __init__(self):
        self.parser = Parser(MEETING_DATE_SENTENCE)
    def __call__(self, text):
        match = self.parser.find(text)
        return None if match is None else datetime.date(**match.fact.as_json).isoformat()


class DividendsRule(BaseYargyRule):
    def __init__(self):
        self.parser_true = Parser(PAY_DIVIDENDS_SENTENCE)
        self.parser_false = Parser(DONT_PAY_DIVIDENDS_SENTENCE)
    def __call__(self, text):
        is_true = self.parser_true.find(text) is not None
        is_false = self.parser_false.find(text) is not None
        if is_true:
            return 'принято решение выплатить дивиденды'
        if is_false:
            return 'принято решение не выплачивать дивиденды'
        return 'вопрос не поднимался'


class BoardOfDirectorsRule(BaseYargyRule):
    def __init__(self):
        self.parser = Parser(BOARD_SENTENCE)
        self.board_presented_parser = Parser(BOARD_PRESENTED)
    def __call__(self, text):
        match = self.board_presented_parser.find(text)
        if not match:
            return []
        match = list(self.parser.findall(text))
        return None if not match else match[-1].fact.names


rules = {
    'Полное наименование': FullNameRule(),
    'Сокращенное наименование': ShortNameRule(),
    'Адрес': AddressRule(),
    'ИНН': INNRule(),
    'ОГРН': OGRNRule(),
    'Дата собрания': MeetingDateRule(),
    'Форма собрания': MeetingFormRule(),
    'Дивиденды': DividendsRule(),
    'Совет директоров': BoardOfDirectorsRule(),
}


def apply_rules_vectorized(events_df, keep_content=True):
    return events_df.assign(**{
        entity_name: np.vectorize(rule, otypes=[object])(events_df.content)
        for entity_name, rule in rules.items()
    }).drop(columns=[] if keep_content else ['content'])


def apply_rules_tqdm(events_df, keep_content=True):
    def apply_rules_to_row(row):
        for entity_name, rule in rules.items():
            row[entity_name] = rule(row.content)
        if not keep_content:
            del row['content']
        return row
    return events_df.progress_apply(apply_rules_to_row, axis=1)


def apply_rules(events_df, keep_content=True, progress=False):
    return (apply_rules_tqdm if progress else apply_rules_vectorized)(events_df, keep_content)
