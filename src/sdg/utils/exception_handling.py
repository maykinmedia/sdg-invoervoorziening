from http import HTTPStatus

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler


from django.core.exceptions import PermissionDenied
from django.http import Http404


def error_message(message):
    new_message = []

    def get_validation_errors(d):
        q = [(d, [])]
        while q:
            n, p = q.pop(0)

            if isinstance(n, dict):
                for k, v in n.items():
                    if isinstance(v, exceptions.ErrorDetail):
                        yield p[:-1], v

                    if isinstance(k, int):
                        k = k + 1

                    q.append((v, p + [str(k)]))

            elif isinstance(n, list):
                for i, v in enumerate(n):
                    q.append((v, p + [str(i + 1)]))

    for x in get_validation_errors(message):
        new_message.append(
            {
                "name": ".".join(x[0]),
                "code": x[1].code,
                "reason": str(x[1]),
            }
        )

    return new_message


def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)
    if response is None:
        return None

    error_messages = error_message(exc.get_full_details())
    http_code_to_message = {v.value: v.description for v in HTTPStatus}

    return_value = {
        "type": exc.__class__.__name__,
        "title": http_code_to_message[response.status_code],
        "status": response.status_code,
    }

    if len(error_messages) > 1:
        return_value["invalidParams"] = error_messages
    else:
        return_value.update(error_messages.pop(0))

    return Response(return_value, status=response.status_code, headers=response.headers)
