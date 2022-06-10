from parsing import get_events


def main():
    companies, events = get_events()
    print(companies[list(companies)[0]])
    print(events[list(events)[0]])


if __name__ == '__main__':
    main()
