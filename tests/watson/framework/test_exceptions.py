# -*- coding: utf-8 -*-
import sys
from watson.framework.exceptions import ApplicationError, NotFoundError, InternalServerError, ExceptionHandler


class TestExceptions(object):

    def test_application_error(self):
        error = ApplicationError('Error', status_code=301)
        assert error.status_code == 301
        assert str(error) == 'Error'

    def test_not_found_error(self):
        error = NotFoundError('Page Not Found')
        assert str(error) == 'Page Not Found'
        assert error.status_code == 404

    def test_not_internal_server_error(self):
        error = InternalServerError('Internal server error')
        assert str(error) == 'Internal server error'
        assert error.status_code == 500


class TestExceptionHandler(object):

    def test_create(self):
        handler = ExceptionHandler({'test': 'blah'})
        assert handler.config['test'] == 'blah'

    def test_call(self):
        handler = ExceptionHandler()
        exc = ApplicationError('Error')
        try:
            raise exc
        except ApplicationError:
            model = handler(sys.exc_info())
            assert model['debug']
            assert model['type'] == 'watson.framework.exceptions.ApplicationError'

    def test_standard_exc(self):
        handler = ExceptionHandler()
        exc = Exception('Error')
        try:
            raise exc
        except Exception:
            model = handler(sys.exc_info())
            assert model['code'] == 500

    def test_raised_from_cause(self):
        handler = ExceptionHandler()
        exc = Exception('Error')
        try:
            try:
                raise exc
            except Exception as e:
                raise ApplicationError('Something', status_code=300) from e
        except ApplicationError:
            model = handler(sys.exc_info())
            assert model['code'] == 300
