# pylint: disable=C0103,R0902
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse


@dataclass
class Company:
    """
    - Полное и сокращенное наименование эмитента
    - Адрес, ИНН, ОГРН эмитента
    """
    id: str
    full_name: str
    short_name: str
    address: str
    inn: str
    ogrn: str

    @staticmethod
    def link_to_id(link: str) -> str:
        return parse_qs(urlparse(link).query)['id'][0]

    @staticmethod
    def id_to_link(identifier: str) -> str:
        return f'https://e-disclosure.ru/portal/company.aspx?id={identifier}'

    @property
    def link(self) -> str:
        return self.id_to_link(self.id)


@dataclass
class Auditor:
    """
    Наименование и ИНН утвержденного аудитора и тип отчетности,
    которую ему поручено проверять (при наличии)
    """
    name: str
    inn: str = None
    report_type: str = None


@dataclass
class Event:
    """
    - Дата и форма собрания
    - Наименование и ИНН утвержденного аудитора + тип отчетности,
      которую ему поручено проверять (при наличии)
    - Утвержденный состав совета директоров (при наличии)
    - Поднимался ли на собрании вопрос о выплате дивидендов и если да,
      то какое решение принято
      (3 варианта: “принято решение выплатить дивиденды”,
      “принято решение не выплачивать дивиденды”, “вопрос не поднимался”)
    """
    id: str
    company_id: str
    date: str
    form: str
    auditor: Auditor = None
    approved_board: list = None
    dividend_decision: str = None
    content: str = field(default=None, repr=False)

    @staticmethod
    def link_to_id(link: str) -> str:
        return parse_qs(urlparse(link).query)['EventId'][0]

    @staticmethod
    def id_to_link(identifier: str) -> str:
        return f'https://e-disclosure.ru/portal/event.aspx?EventId={identifier}'

    @property
    def link(self) -> str:
        return self.id_to_link(self.id)
