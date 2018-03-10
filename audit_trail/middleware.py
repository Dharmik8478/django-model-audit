from threading import local

_thread_locals = local()

class AuditMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.process_response(request)
        return response

    def process_request(self, request):
        _thread_locals.request = request

    def process_response(self, request, response=None):
        response = self.get_response(request) if not response else response
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

    @classmethod
    def get_request(self):
        return _thread_locals.request if hasattr(_thread_locals, 'request')        else None
