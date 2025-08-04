from collections import defaultdict

events = defaultdict(list)


def post_event(event_name: str, **kwargs) -> dict[str, Exception]:
    errors = {}

    for fn in events[event_name]:
        try:
            fn(**kwargs)
        except Exception as e:
            errors[fn.__name__] = e

    return errors


def add_event(event_name: str, function):
    events[event_name].append(function)
