from rest_framework.views import exception_handler
from rest_framework.response import Response


def vilapay_exception_handler(exc, context):
    """
    Wrap DRF error responses to always include the HTTP status code in the body:

        {
            "status_code": 405,
            "detail": "Method \"GET\" not allowed."
        }
    """
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        # DRF already puts detail / non-field errors in the body.
        # We just add the numeric status code at the top level.
        if isinstance(data, dict):
            data["status_code"] = response.status_code
        else:
            # e.g. list of validation errors — wrap it
            response.data = {
                "status_code": response.status_code,
                "errors": data,
            }

    return response
