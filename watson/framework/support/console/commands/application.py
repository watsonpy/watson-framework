# -*- coding: utf-8 -*-
import os
import stat
import sys
from wsgiref import util
from string import Template
from watson.common.contextmanagers import ignored
from watson.common.imports import load_definition_from_string
from watson.console import ConsoleError, colors
from watson.console import command
from watson.di import ContainerAware
from watson.http.messages import Request
from watson.dev.server import make_dev_server


class CreateApplication(command.Base, ContainerAware):
    name = 'newproject'
    help = 'Creates a new project, defaults to the current working directory.'
    arguments = [
        {'dest': 'project_name', 'help': 'The name of the project to create.'},
        {'dest': 'app_name', 'help': 'The name of the application to create.'},
        (('-d', '--dir'), {'help': 'The directory to create the project in.'}),
        (('-o', '--override'),
         {'action': 'store_const', 'help': 'Override any existing project in the path.', 'const': 1}),
    ]

    def execute(self):
        if not self.parsed_args.project_name:
            raise ConsoleError('No project name specified')
        if not self.parsed_args.app_name:
            raise ConsoleError('No app name specified')
        project_name = self.parsed_args.project_name
        app_name = self.parsed_args.app_name
        if self.parsed_args.dir:
            root = os.path.abspath(self.parsed_args.dir)
        else:
            root = os.getcwd()
        basepath = os.path.join(root, project_name)
        paths = [
            basepath,
            os.path.join(basepath, app_name),
            os.path.join(basepath, app_name, 'config'),
            os.path.join(basepath, app_name, 'controllers'),
            os.path.join(basepath, app_name, 'views'),
            os.path.join(basepath, app_name, 'views', 'index'),
            os.path.join(basepath, 'data'),
            os.path.join(basepath, 'data', 'cache'),
            os.path.join(basepath, 'data', 'logs'),
            os.path.join(basepath, 'data', 'uploads'),
            os.path.join(basepath, 'public'),
            os.path.join(basepath, 'public', 'css'),
            os.path.join(basepath, 'public', 'img'),
            os.path.join(basepath, 'public', 'js'),
            os.path.join(basepath, 'tests'),
            os.path.join(basepath, 'tests', app_name),
            os.path.join(basepath, 'tests', app_name, 'controllers'),
        ]
        files = [
            (os.path.join(basepath, app_name, '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'app.py'), APP_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'config', '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'config', 'prod.py.dist'),
             PROD_CONFIG_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'config', 'dev.py.dist'),
             DEV_CONFIG_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'config', 'config.py'),
             DEV_CONFIG_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'config', 'routes.py'),
             ROUTES_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'controllers', '__init__.py'),
             SAMPLE_CONTROLLER_INIT_TEMPLATE),
            (os.path.join(basepath, app_name, 'controllers', 'index.py'),
             SAMPLE_CONTROLLER_TEMPLATE),
            (os.path.join(basepath, app_name, 'views', 'index', 'get.html'),
             SAMPLE_VIEW_TEMPLATE),
            (os.path.join(basepath, 'tests', '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, 'tests', app_name, '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, 'tests', app_name,
             'controllers', '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, 'tests', app_name,
             'controllers', 'test_index.py'), SAMPLE_TEST_SUITE),
            (os.path.join(basepath, 'console.py'), CONSOLE_TEMPLATE),
        ]
        for path in paths:
            try:
                os.mkdir(path)
            except:
                if not self.parsed_args.override:
                    raise ConsoleError(
                        'Project already exists at {0}'.format(basepath))
        for filename, contents in files:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(
                        Template(
                            contents).safe_substitute(
                                app_name=app_name))
            except:
                if not self.parsed_args.override:
                    raise ConsoleError(
                        'File {0} already exists.'.format(filename))
        st = os.stat(files[-1][0])
        os.chmod(files[-1][0], st.st_mode | stat.S_IEXEC)


class RunDevelopmentServer(command.Base, ContainerAware):
    name = 'rundev'
    help = 'Runs the development server for the current application.'

    def execute(self):
        app_dir = os.environ['APP_DIR']
        app_module = os.environ['APP_MODULE']
        script_dir = os.environ['SCRIPT_DIR']
        public_dir = os.environ['PUBLIC_DIR']
        os.chdir(app_dir)
        app = load_definition_from_string('{0}.app.application'.format(
            app_module))
        make_dev_server(app,
                        do_reload=True,
                        script_dir=script_dir,
                        public_dir=public_dir)


class RunTests(command.Base, ContainerAware):
    name = 'runtests'
    help = 'Runs the unit tests for the project.'

    def execute(self):
        try:
            app_module = os.environ['APP_MODULE']
            test_runner = None
            cli_args = ''
            sys.argv = [sys.argv.pop(0)]
            try:
                import pytest
                test_runner = 'pytest'
                cli_args = '--cov {0}'.format(app_module)
            except:
                with ignored(ImportError):
                    import nose
                    test_runner = 'nose'
                    cli_args = '--cover-package={0}'.format(app_module)
            if test_runner:
                sys.modules[test_runner].main(cli_args.split(' '))
            else:
                raise ConsoleError(
                    "You must install either 'nose' or 'py.test' to run the unit tests.")
        except:
            _no_application_error()


class Routes(command.Base, ContainerAware):
    name = 'routes'
    help = 'Aids in the debugging of routes associated.'
    arguments = [
        (('-u', '--url'),
         {'help': 'Validate the specified url against the router.', 'required': False}),
        (('-m', '--method'),
         {'help': 'The http request method.', 'required': False}),
        (('-f', '--format'),
         {'help': 'The http request format.', 'required': False}),
        (('-s', '--server'), {'help': 'The hostname.', 'required': False}),
    ]

    def execute(self):
        try:
            router = self.container.get('router')
            if not router.routes:
                raise ConsoleError(
                    'There are no routes associated with the application.')
            if self.parsed_args.url:
                environ = {}
                util.setup_testing_defaults(environ)
                environ.update({
                    'REQUEST_METHOD': self.parsed_args.method or 'GET',
                    'HTTP_ACCEPT': self.parsed_args.format or 'text/html',
                    'PATH_INFO': self.parsed_args.url,
                    'SERVER_NAME': self.parsed_args.server or '127.0.0.1'
                })
                request = Request.from_environ(environ)
                matches = router.matches(request)
                if matches:
                    sys.stdout.write(
                        colors.header('Displaying {0} matching routes for the application:\n'.format(len(matches))))
                    for match in matches:
                        sys.stdout.write(
    '{0}\t\t\{1}\t\t{2}\n'.format(
        colors.ok_green(
            match.route.name),
             match.route.path,
             match.route.regex.pattern))
                else:
                    raise ConsoleError('There are no matching routes.')
            else:
                sys.stdout.write(
                    colors.header('Displaying {0} routes for the application:\n'.format(len(router))))
                for name, route in router:
                    sys.stdout.write('{0}\t\t{1}\n'.format(name, route.path))
        except ConsoleError:
            raise
        except:
            _no_application_error()


def _no_application_error():
    raise ConsoleError(
    'No watson application can be found, are you sure you\'re in the correct directory?')


BLANK_PY_TEMPLATE = """# -*- coding: utf-8 -*-
"""

APP_PY_TEMPLATE = """# -*- coding: utf-8 -*-
from watson.framework import applications
from ${app_name}.config import config

application = applications.Http(config)
"""

ROUTES_PY_TEMPLATE = """# -*- coding: utf-8 -*-
routes = {
    'index': {
        'path': '/',
        'options': {'controller': '${app_name}.controllers.Index'}
    }
}
"""

PROD_CONFIG_PY_TEMPLATE = """# -*- coding: utf-8 -*-
from ${app_name}.config.routes import routes


debug = {
    'enabled': False
}
"""

DEV_CONFIG_PY_TEMPLATE = """# -*- coding: utf-8 -*-
from ${app_name}.config.routes import routes


debug = {
    'enabled': True
}

"""

SAMPLE_CONTROLLER_INIT_TEMPLATE = """# -*- coding: utf-8 -*-
from ${app_name}.controllers.index import Index


__all__ = ['Index']
"""

SAMPLE_CONTROLLER_TEMPLATE = """# -*- coding: utf-8 -*-
from watson import framework
from watson.framework import controllers


class Index(controllers.Rest):
    def GET(self):
        return 'Welcome to Watson v{0}!'.format(framework.__version__)
"""

SAMPLE_VIEW_TEMPLATE = """<!DOCTYPE html>
<html>
    <head>
        <title>Welcome to Watson!</title>
    </head>
    <body>
        <h1>{{ content }}</h1>
        <p>You are now on your way to creating your first application using Watson.</p>
        <p>Read more about Watson in <a href="http://watson-framework.readthedocs.org/">the documentation.</a>
    </body>
</html>
"""

SAMPLE_TEST_SUITE = """# -*- coding: utf-8 -*-
from watson import framework
from ${app_name}.controllers.index import Index


class TestSuiteIndex(object):
    def test_get(self):
        index = Index()
        assert index.GET() == 'Welcome to Watson v{0}!'.format(framework.__version__)
"""

CONSOLE_TEMPLATE = """#!/usr/bin/env python
import os
import sys

import os
import sys

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))
os.environ.update({
    'APP_MODULE': '${app_name}',
    'APP_DIR': os.path.join(SCRIPT_DIR, '${app_name}'),
    'PUBLIC_DIR': os.path.join(SCRIPT_DIR, 'public'),
    'SCRIPT_DIR': SCRIPT_DIR
})
try:
    import watson
except:
    sys.stdout.write('You must have Watson installed, please run `pip install watson-framework`\\n')
    sys.exit(1)

from watson.framework import applications
from ${app_name}.config import config

if __name__ == '__main__':
    os.chdir(os.environ['APP_DIR'])
    application = applications.Console(config)
    application()
"""
