import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    """
    Adds a X-Process-Time header to the response with the time taken to process the request.
    """

    def __init__(self, app):
        super(ProcessTimeHeaderMiddleware, self).__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Adds the X-Process-Time header to the response.

        :param request: The request that is being processed.
        :type request: fastapi.Request
        :param call_next: A function that calls the next middleware or the endpoint.
        :type call_next: typing.Callable[[fastapi.Request], typing.Awaitable[fastapi.Response]]
        :return: The response with the added X-Process-Time header.
        :rtype: fastapi.Response
        """
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
