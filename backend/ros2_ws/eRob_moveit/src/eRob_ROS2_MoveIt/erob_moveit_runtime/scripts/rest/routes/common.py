"""HTTP serialization only; transport-neutral APIs own operation outcomes."""
from flask import jsonify
from runtime_api.contracts import ApiResponse


def to_http(response: ApiResponse):
    result = jsonify(response.body)
    result.headers['X-Request-ID'] = response.body['request_id']
    return result, response.status


def install_http_contract(app):
    """Install correlation and JSON transport errors once for all API blueprints."""
    import logging
    import re
    from uuid import uuid4
    from flask import g, request
    from werkzeug.exceptions import HTTPException
    from runtime_api.contracts import request_context, response_error, exception_response
    logger = logging.getLogger(__name__)

    @app.before_request
    def begin_runtime_request():
        supplied = request.headers.get('X-Request-ID', '')
        request_id = supplied if re.fullmatch(r'[A-Za-z0-9._-]{1,128}', supplied) else uuid4().hex
        scope = request_context(request_id, f'http:{request.method} {request.url_rule or request.path}')
        scope.__enter__()
        g.runtime_request_scope = scope
        g.runtime_request_id = request_id

    @app.after_request
    def correlate_runtime_response(response):
        if 'runtime_request_id' in g:
            response.headers['X-Request-ID'] = g.runtime_request_id
        return response

    @app.teardown_request
    def end_runtime_request(error):
        scope = g.pop('runtime_request_scope', None)
        if scope is not None:
            scope.__exit__(None, None, None)

    @app.errorhandler(Exception)
    def runtime_transport_error(error):
        if isinstance(error, HTTPException):
            details = {'cause': str(error.__cause__)} if error.__cause__ else {}
            return to_http(response_error(error.description, error.code,
                           code='invalid_json' if error.code == 400 else None,
                           source='transport', details=details))
        logger.exception('Unhandled HTTP transport error')
        return to_http(exception_response(error))
