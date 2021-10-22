from collections import defaultdict

events = defaultdict(list)


def post_event(event_name: str, **kwargs):
    for fn in events[event_name]:
        fn(**kwargs)


def add_event(event_name: str, function):
    events[event_name].append(function)
