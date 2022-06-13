import pandas as pd

from loading import fetch_filtered_events
from parsing import apply_rules


def fetch_and_save_events(path: str):
    events_df = fetch_filtered_events()
    events_df.to_json(path)


def main():
    # fetch_and_save_events('data/raw_events.json')
    events_df = pd.read_json('data/raw_events.json')
    events_df = apply_rules(events_df, keep_content=False, progress=True)
    events_df.to_csv('result.csv')


if __name__ == '__main__':
    main()
