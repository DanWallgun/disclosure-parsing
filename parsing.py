import re
import typing

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from models import Company, Auditor, Event


def parse_company_page(company_id):
    company_page = BeautifulSoup(
        requests.get(Company.id_to_link(company_id)).content,
        'html.parser'
    )

    general_info = dict(
        tuple(td.text for td in row.find_all('td'))
        for row in company_page.find('div', text='Общие сведения').next_sibling.find_all('tr')
    )

    return Company(
        id=company_id,
        full_name=general_info['Полное наименование компании'],
        short_name=general_info['Сокращенное наименование компании'],
        address=general_info['Место нахождения'],
        inn=general_info['ИНН'],
        ogrn=general_info['Номер Государственной регистрации (ОГРН)'],
    )


def parse_event_page(event_id):
    event_page = BeautifulSoup(requests.get(Event.id_to_link(event_id)).content, 'html.parser')

    company_id = Company.link_to_id(
        event_page.find('ul', id='cssmenu').findChild().findChild().get('href')
    )

    date = event_page.find('span', class_='date').text
    content = event_page.find('div', id='cont_wrap').find('div').find_next('div').text

    form_match = re.search(r'Форма проведения [^:]+: (.+)', content)
    form = None if form_match is None else form_match[1]
    auditor_match = re.search(r'Утвердить аудитором Общества на \d+ год (.+)', content)
    auditor_name = None if auditor_match is None else auditor_match[1]
    approved_board_match = re.search(
        (
            r'Избрать Совет директоров .+ численностью \d+ '
            r'человек в составе:\n((?:.|\n)+)\nРезультаты'
        ),
        content
    )
    approved_board = None if approved_board_match is None else approved_board_match[1].split('\n')

    return Event(
        id=event_id,
        company_id=company_id,
        date=date,
        form=form,
        auditor=Auditor(name=auditor_name),
        approved_board=approved_board,
        content=content,
    )


def parse_search_results(search_results, limit: int = None, disable_tqdm: bool = True):
    companies: typing.Dict[str, Company] = {}
    events: typing.Dict[str, Event] = {}
    event_rows = search_results.find_all('tr')[:-2]
    if limit is not None:
        event_rows = event_rows[:limit]
    for row in tqdm(event_rows, disable=disable_tqdm):
        a_tag = row.find('a')
        company_id = Company.link_to_id(a_tag.get('href'))
        event_id = Event.link_to_id(a_tag.find_next('a').get('href'))
        if company_id not in companies:
            companies[company_id] = parse_company_page(company_id)
        events[event_id] = parse_event_page(event_id)
    return companies, events


def get_events():
    url = 'https://e-disclosure.ru/poisk-po-soobshheniyam'

    response = requests.post(
        url,
        params={
            'lastPageSize': 2147483647,
            'lastPageNumber': 1,
            'query': '',
            'queryEvent': '',
            'eventTypeTerm': '',
            'radView': 1,
            'eventTypeCheckboxGroup': 101, # Решения общих собраний участников (акционеров)
            'dateStart': '01.04.2021',
            'dateFinish': '30.06.2021',
            'textfieldEvent': '',
            'radReg': 'Regions',
            'districtsCheckboxGroup': -1,
            'regionsCheckboxGroup': 77, # Москва
            'branchClientLog': '-1,1,14,21,3,2,19,6,8,15,7,16,22,18,12,10,17,20,13,11,4,5,9',
            'branchesCheckboxGroup': -1,
            'textfieldCompany': '',
        }
    )

    search_results = BeautifulSoup(response.content, 'html.parser')
    return parse_search_results(search_results, 5, disable_tqdm=False)
