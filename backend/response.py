from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


class _Response(Response):
    def __init__(self, status="ok", status_code=HTTP_200_OK, *args, **kwargs):
        response = {"status": status}
        for key, val in kwargs.items():
            response[key] = val
        super(_Response, self).__init__(data=response, status=status_code)


class SuccessResponse(_Response):
    def __init__(self, status_code=HTTP_200_OK, *args, **kwargs):
        super(SuccessResponse, self).__init__(
            status="ok", status_code=status_code, **kwargs
        )


class ErrorResponse(_Response):
    def __init__(self, status_code=HTTP_400_BAD_REQUEST, *args, **kwargs):
        super(ErrorResponse, self).__init__(
            status="err", status_code=status_code, **kwargs
        )
