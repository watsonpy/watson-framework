# -*- coding: utf-8 -*-
import os
from pprint import pprint
import stat
import sys
from wsgiref import util
from string import Template
from watson.common.contextmanagers import suppress
from watson.console import ConsoleError, colors, command
from watson.console.decorators import arg
from watson.di import ContainerAware
from watson.http.messages import Request


class Project(command.Base, ContainerAware):
    """Creating and maintaining Watson projects.

    Example:

    .. code-block::

        ./console.py dev runserver
    """

    __ioc_definition__ = {
        'property': {
            'router': 'router',
            'application_config': 'application.config'
        }
    }

    @arg('override', action='store_const', const=1, optional=True)
    @arg('component_based', action='store_const', const=1, optional=True)
    @arg('dir', optional=True)
    def new(self, name, app_name, dir, override, component_based):
        """Creates a new project, defaults to the current working directory.

        Args:
            name: The name of the project
            app_name: The name of the application to create
            dir: The directory to create the project in
            override: Override any existing project in the path
            component_based: Create component based structure
        """
        if dir:
            root = os.path.abspath(dir)
            if not os.path.exists(root):
                raise ConsoleError('Directory {} not found'.format(root))
        else:
            root = os.getcwd()
        basepath = os.path.join(root, name)
        paths = [
            basepath,
            os.path.join(basepath, app_name),
            os.path.join(basepath, 'data'),
            os.path.join(basepath, 'data', 'cache'),
            os.path.join(basepath, 'data', 'logs'),
            os.path.join(basepath, 'data', 'uploads'),
            os.path.join(basepath, 'public'),
            os.path.join(basepath, 'public', 'css'),
            os.path.join(basepath, 'public', 'img'),
            os.path.join(basepath, 'public', 'js'),
            os.path.join(basepath, 'static'),
            os.path.join(basepath, 'static', 'js'),
            os.path.join(basepath, 'static', 'scss'),
            os.path.join(basepath, 'tests'),
        ]
        files = [
            (os.path.join(basepath, 'console.py'), CONSOLE_TEMPLATE),
            (os.path.join(basepath, '.editorconfig'), EDITOR_CONFIG_TEMPLATE),
            (os.path.join(basepath, '.gitignore'), GITIGNORE_TEMPLATE),
            (os.path.join(basepath, 'requirements.txt'), REQUIREMENTS_TEMPLATE),
            (os.path.join(basepath, 'README.md'), ''),
            (os.path.join(basepath, 'public', 'robots.txt'), ROBOTS_TEMPLATE),
            (os.path.join(basepath, app_name, '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, app_name, 'app.py'), APP_PY_TEMPLATE),
            (os.path.join(basepath, 'tests', '__init__.py'), BLANK_PY_TEMPLATE),
            (os.path.join(basepath, 'tests', app_name, '__init__.py'), BLANK_PY_TEMPLATE),
        ]

        if not component_based:
            paths.extend([
                os.path.join(basepath, app_name, 'config'),
                os.path.join(basepath, app_name, 'controllers'),
                os.path.join(basepath, app_name, 'views'),
                os.path.join(basepath, app_name, 'views', 'index'),
                os.path.join(basepath, 'tests', app_name),
                os.path.join(basepath, 'tests', app_name, 'controllers'),
            ])
            files.extend([
                (os.path.join(basepath, app_name, 'config', 'base.py'),
                 SIMPLE_CONFIG_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'config', 'routes.py'),
                 SIMPLE_ROUTES_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'config', 'dependencies.py'),
                 DEPENDENCIES_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'controllers', '__init__.py'),
                 SIMPLE_SAMPLE_CONTROLLER_INIT_TEMPLATE),
                (os.path.join(basepath, app_name, 'controllers', 'index.py'),
                 SAMPLE_CONTROLLER_TEMPLATE),
                (os.path.join(basepath, app_name, 'views', 'index', 'get.html'),
                 SAMPLE_VIEW_TEMPLATE),
                (os.path.join(basepath, 'tests', app_name,
                 'controllers', '__init__.py'), BLANK_PY_TEMPLATE),
                (os.path.join(basepath, 'tests', app_name,
                 'controllers', 'test_index.py'), SIMPLE_SAMPLE_TEST_SUITE),
            ])
        else:
            paths.extend([
                os.path.join(basepath, app_name, 'common'),
                os.path.join(basepath, app_name, 'config'),
                os.path.join(basepath, app_name, 'common', 'controllers'),
                os.path.join(basepath, app_name, 'common', 'views'),
                os.path.join(basepath, app_name, 'common', 'views', 'index'),
                os.path.join(basepath, 'tests', app_name),
                os.path.join(basepath, 'tests', app_name, 'common'),
                os.path.join(basepath, 'tests', app_name, 'common', 'controllers'),
            ])
            files.extend([
                (os.path.join(basepath, app_name, 'config', '__init__.py'),
                 BLANK_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'config', 'base.py'),
                 COMPONENT_CONFIG_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'config', 'dependencies.py'),
                 DEPENDENCIES_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'common', '__init__.py'),
                 BLANK_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'common', 'routes.py'),
                 COMPONENT_ROUTES_PY_TEMPLATE),
                (os.path.join(basepath, app_name, 'common', 'controllers', '__init__.py'),
                 COMPONENT_SAMPLE_CONTROLLER_INIT_TEMPLATE),
                (os.path.join(basepath, app_name, 'common', 'controllers', 'index.py'),
                 SAMPLE_CONTROLLER_TEMPLATE),
                (os.path.join(basepath, app_name, 'common', 'views', 'index', 'get.html'),
                 SAMPLE_VIEW_TEMPLATE),
                (os.path.join(basepath, 'tests', app_name, 'common',
                 'controllers', '__init__.py'), BLANK_PY_TEMPLATE),
                (os.path.join(basepath, 'tests', app_name, 'common',
                 'controllers', 'test_index.py'), COMPONENT_SAMPLE_TEST_SUITE),
            ])

        for path in paths:
            try:
                os.mkdir(path)
            except:
                if not override:
                    raise ConsoleError(
                        'Project already exists at {0}'.format(basepath))
        for filename, contents in files:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(
                        Template(
                            contents).safe_substitute(app_name=app_name))
            except:
                if not override:
                    raise ConsoleError(
                        'File {0} already exists.'.format(filename))
        st = os.stat(files[-1][0])
        os.chmod(files[0][0], st.st_mode | stat.S_IEXEC)
        self.write('Project {} created at {}'.format(name, root))

    @arg()
    def config(self):
        """Prints out the applications configuration.
        """
        pprint(self.application_config)

    @arg()
    def test(self):
        """Runs the unit tests for the project.
        """
        current_directory = os.getcwd()
        os.chdir(os.path.join(current_directory, '..'))
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
                with suppress(ImportError):
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
        os.chdir(current_directory)

    @arg('path', optional=True)
    @arg('method', optional=True)
    @arg('format', optional=True)
    @arg('server', optional=True)
    def routes(self, path, method, format, server):
        """Aids in the debugging of routes associated.

        Args:
            path: Validate the specified path against the router
            method: The http request method
            format: The http request format
            server: The hostname of the request
        """
        try:
            router = self.router
            if not router.routes:
                raise ConsoleError(
                    'There are no routes associated with the application.')
            if path:
                environ = {}
                util.setup_testing_defaults(environ)
                server = server or '127.0.0.1'
                environ.update({
                    'REQUEST_METHOD': method or 'GET',
                    'HTTP_ACCEPT': format or 'text/html',
                    'PATH_INFO': path,
                    'SERVER_NAME': server,
                    'HTTP_HOST': server
                })
                request = Request.from_environ(environ)
                matches = [match for match in router.matches(request)]

                if matches:
                    longest_route = max([match.route.name for match in matches], key=len)
                    self.write(
                        colors.header('Displaying {} matching routes for {}:\n'.format(
                            len(matches), request.url)))
                    for match in matches:
                        route = match.route
                        self.write('{0}\t{1}\n'.format(
                            route.name.rjust(len(longest_route)), route.path))
                else:
                    raise ConsoleError('There are no matching routes.')
            else:
                self.write(colors.header('Displaying {0} routes for the application:\n'.format(len(router))))
                longest_route = max(router, key=len)
                for name, route in router:
                    self.write('{0}\t{1}\n'.format(
                        name.rjust(len(longest_route[0])), route.path))
        except ConsoleError:
            raise
        except Exception as e:
            raise e
            _no_application_error()


def _no_application_error():
    raise ConsoleError(
        'No watson application can be found, are you sure you\'re in the correct directory?')


EDITOR_CONFIG_TEMPLATE = """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{py,md,ini,rst,html}]
indent_style = space
indent_size = 4

[*.{css,scss,json,yml,js}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
"""

GITIGNORE_TEMPLATE = """# OSX & Workspace
.DS_STORE
.cache/v/

### Python ###
*.py[cod]

# C extensions
*.so

# Packages
*.egg
*.egg-info
dist
build
eggs
parts
bin
var
sdist
develop-eggs
.installed.cfg
lib
lib64
__pycache__
*.pyc

# Installer logs
pip-log.txt

# Unit test / coverage reports
.coverage
.tox
nosetests.xml
tests/_coverage

# Translations
*.mo

# Documentation
docs/_build
"""


ROBOTS_TEMPLATE = """User-agent: *
Disallow:
"""

REQUIREMENTS_TEMPLATE = """# Framework requirements
watson-framework

# Project requirements
pytest
pytest-cov
"""


BLANK_PY_TEMPLATE = """# -*- coding: utf-8 -*-
"""

APP_PY_TEMPLATE = """# -*- coding: utf-8 -*-
from watson.framework import applications
from ${app_name}.config import base as config

application = applications.Http(config)
"""

SIMPLE_ROUTES_PY_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"Create routes for your application here.
\"\"\"
routes = {
    'index': {
        'path': '/',
        'options': {'controller': '${app_name}.controllers.Index'}
    }
}
"""

COMPONENT_ROUTES_PY_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"Create routes for your application here.
\"\"\"

routes = {
    'index': {
        'path': '/',
        'options': {'controller': '${app_name}.common.controllers.Index'}
    }
}
"""

SIMPLE_CONFIG_PY_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"Define and extend configuration settings for your application.
\"\"\"

import os
from ${app_name}.config.routes import routes  # noqa
from ${app_name}.config.dependencies import dependencies  # noqa


debug = {
    'enabled': os.environ.get('DEV_ENV', False)
}
"""

COMPONENT_CONFIG_PY_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"Define and extend configuration settings for your application.
\"\"\"

import os
from ${app_name}.config.dependencies import dependencies  # noqa

components = [
    '${app_name}.common'
]

debug = {
    'enabled': os.environ.get('DEV_ENV', False)
}
"""

DEPENDENCIES_PY_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"Define container dependencies.
\"\"\"
dependencies = {
}
"""

SIMPLE_SAMPLE_CONTROLLER_INIT_TEMPLATE = """# -*- coding: utf-8 -*-
from ${app_name}.controllers.index import Index


__all__ = ['Index']
"""

COMPONENT_SAMPLE_CONTROLLER_INIT_TEMPLATE = """# -*- coding: utf-8 -*-
from ${app_name}.common.controllers.index import Index


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

SIMPLE_SAMPLE_TEST_SUITE = """# -*- coding: utf-8 -*-
from watson import framework
from ${app_name}.controllers.index import Index


class TestSuiteIndex(object):
    def test_get(self):
        index = Index()
        assert index.GET() == 'Welcome to Watson v{0}!'.format(framework.__version__)
"""

COMPONENT_SAMPLE_TEST_SUITE = """# -*- coding: utf-8 -*-
from watson import framework
from ${app_name}.common.controllers.index import Index


class TestSuiteIndex(object):
    def test_get(self):
        index = Index()
        assert index.GET() == 'Welcome to Watson v{0}!'.format(framework.__version__)
"""

CONSOLE_TEMPLATE = """#!/usr/bin/env python
import os
import sys

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))
os.environ.update({
    'APP_MODULE': '${app_name}',
    'APP_SETTINGS': '${app_name}.config.base',
    'APP_DIR': os.path.join(SCRIPT_DIR, '${app_name}'),
    'PUBLIC_DIR': os.path.join(SCRIPT_DIR, 'public'),
    'SCRIPT_DIR': SCRIPT_DIR
})
os.chdir(os.environ['APP_DIR'])

try:
    from watson.framework import applications
    from watson.common import imports
except:
    sys.stdout.write(
        'You must have Watson installed, please run `pip install watson-framework`\\n')
    sys.exit(1)


if __name__ == '__main__':
    config = imports.import_module(os.environ['APP_SETTINGS'])
    application = applications.Console(config)
    application()
"""
