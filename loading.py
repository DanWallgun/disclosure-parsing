import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from models import Event


def fetch_event_content(event_id):
    event_page = BeautifulSoup(requests.get(Event.id_to_link(event_id)).content, 'html.parser')
    return event_page.find('div', id='cont_wrap').find('div').find_next('div').text


def fetch_filtered_events(disable_tqdm=True, **kwargs):
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
    params.update(kwargs)
    url = 'https://e-disclosure.ru/poisk-po-soobshheniyam'
    response = requests.post(url, params=params)
    search_results = BeautifulSoup(response.content, 'html.parser')

    rows = []
    for row in tqdm(search_results.find_all('tr')[:-2], disable=disable_tqdm):
        event_id = Event.link_to_id(row.find('a').find_next('a').get('href'))
        rows.append([event_id, fetch_event_content(event_id)])

    return pd.DataFrame(data=rows, columns=['event_id', 'content'])
