# pylint: disable=R0903,W0231
from abc import ABC, abstractmethod
import datetime
import re

import numpy as np
from yargy import Parser

from yargy_rules import MEETING_FORM_SENTENCE, MEETING_DATE_SENTENCE


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


rules = {
    'Полное наименование': FullNameRule(),
    'Сокращенное наименование': ShortNameRule(),
    'Адрес': AddressRule(),
    'ИНН': INNRule(),
    'ОГРН': OGRNRule(),
    'Дата собрания': MeetingDateRule(),
    'Форма собрания': MeetingFormRule(),
}


def apply_rules(events_df, keep_content=True):
    return events_df.assign(**{
        entity_name: np.vectorize(rule, otypes=[object])(events_df.content)
        for entity_name, rule in rules.items()
    }).drop(columns=[] if keep_content else ['content'])
