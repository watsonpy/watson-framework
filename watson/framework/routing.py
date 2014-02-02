# -*- coding: utf-8 -*-
import collections
import re
from watson.http import REQUEST_METHODS, MIME_TYPES
from watson.common.imports import get_qualified_name


class Router(object):

    """Responsible for maintaining a list of routes.

    Attributes:
        routes (OrderedDict): A dict of routes
    """
    __slots__ = ('routes')

    def __init__(self, routes=None):
        if not routes:
            routes = {}
        self.routes = collections.OrderedDict()
        if isinstance(routes, dict):
            self._from_dict(routes)
        else:
            self._from_list(routes)

    def matches(self, request):
        """Match a request against all the routes.

        Args:
            request (watson.http.messages.Request): The request to match.

        Returns:
            A list of RouteMatch namedtuples.
        """
        for name, route in self.routes.items():
            route_match = route.match(request)
            if route_match:
                yield route_match

    def assemble(self, route_name, **kwargs):
        """Converts the route into a path.

        Applies any keyword arguments as params on the route. This is a
        convenience method for accessing the assemble method on an individual
        route.

        Args:
            route_name (string): The name of the route

        Raises:
            KeyError if the route does not exist on the router.
        """
        if route_name in self:
            return self.routes[route_name].assemble(**kwargs)
        else:
            raise KeyError(
                'No route named {0} can be found.'.format(route_name))

    def add_definition(self, definition):
        """Converts a route definition into a route.

        Args:
            definition (dict): The definition to add.
        """
        route = Route(**definition)
        self.add_route(route)

    def add_route(self, route):
        """Adds an instantiated route to the router.

        Args:
            route (watson.framework.routing.Route): The route to add.
        """
        self.routes[route.name] = route

    def sort(self):
        self.routes = collections.OrderedDict(
            reversed(sorted(self.routes.items(),
                     key=lambda route: route[1]['priority'])))

    # Internals

    def __contains__(self, route_name):
        return route_name in self.routes

    def _from_list(self, routes):
        # Creates a router from a list of route objects or definitions.
        for route_definition in routes:
            route = route_definition
            if not isinstance(route_definition, Route):
                route = Route(**route_definition)
            self.add_route(route)
            self._create_child_routes(route_definition, route)

    def _from_dict(self, routes):
        # Creates a router from a dict of named route definitions.
        for name, route_definition in routes.items():
            route = route_definition
            if not isinstance(route_definition, Route):
                route = Route(name=name, **route_definition)
            self.add_route(route)
            self._create_child_routes(route_definition, route)
        self.sort()

    def _create_child_routes(self, definition, parent_route):
        if 'children' in definition:
            for name, child_definition in definition['children'].items():
                child_definition['path'] = '{0}{1}'.format(
                    parent_route.path,
                    child_definition['path'])
                name = '{0}/{1}'.format(parent_route.name, name)
                route = Route(name=name, **child_definition)
                self.add_route(route)
                self._create_child_routes(child_definition, route)

    def __len__(self):
        return len(self.routes)

    def __iter__(self):
        for name, route in self.routes.items():
            yield name, route

    def __repr__(self):
        return (
            '<{0} routes:{1}>'.format(
                get_qualified_name(self),
                len(self.routes))
        )


# route: The matched route
# params: The parameters that have been matched
RouteMatch = collections.namedtuple('RouteMatch', 'route params')


class Route(dict):

    """A route is designed to validate a request against a specific path.

    Example:

    .. code-block:: python

        'users': {
            'path': '/users[/:id]',
            'options': {
                'controller': 'my.first.Controller',
                'action': 'list'
            }
        }

    Attributes:
        regex (SRE_Pattern): The regular expression to match, generated from the path
        segments (list): A list of segments from the path
    """
    regex = None
    segments = None

    @property
    def name(self):
        """Convenience method to return the name of the route.
        """
        return self['name']

    @property
    def path(self):
        """Convenience method to return the path of the route.
        """
        return self['path']

    @property
    def options(self):
        """Convenience method to return the options of the route.
        """
        return self['options']

    def __init__(self, name, path, *args, **kwargs):
        """Initializes a new route.

        Args:
            name (string): The name of the route
            path (string): The path to match

        Optional Args:
            accepts (list|tuple): A list of accepted http request methods
            defaults (dict): A dict of defaults for optional params
            requires (dict): A dict of required params to match
            subdomain (string): The subdomain to match
        """
        kwargs.update({
            'name': name,
            'path': path,
            'requires': kwargs.get('requires', {})
        })
        super(Route, self).__init__(*args, **kwargs)
        if 'priority' not in kwargs:
            self['priority'] = 1
        if 'regex' in kwargs:
            self.regex = re.compile(kwargs['regex'])
        if not self.regex:
            self.regex, self.segments = self.__create_regex_from_segment_path(
                self['path'], self.get('requires', {}))
        if 'format' in self.get('requires', ()):
            self['format'] = re.compile(self['requires']['format'])

    def match(self, request):
        """Matches a request against the route.

        Args:
            request (watson.http.messages.Request): The request to match.

        Returns:
            A RouteMatch namedtuple containing the keys route, params, matched.
        """
        params = self.get('defaults', {}).copy()
        if request.method not in self.get('accepts', REQUEST_METHODS):
            return None
        if 'subdomain' in self:
            subdomains = self.get('subdomain')
            if isinstance(subdomains, (list, tuple)):
                if request.url.subdomain not in subdomains:
                    return None
            elif request.url.subdomain != self.get('subdomain'):
                return None
        accept_format = request.headers.get('Accept')
        formats = None
        if accept_format:
            formats = [format for format in MIME_TYPES if
                       accept_format in MIME_TYPES[format]]
            if formats:
                params['format'] = formats[0]
        if 'format' in self and formats:
            if self['format'].match(formats[0]):
                params['format'] = formats[0]
            else:
                return None
        matches = self.regex.match(request.url.path)
        if self['requires'] and request.get:
            if all(key in request.get for key in self['requires']):
                params.update((k, v)
                              for k, v in request.get.items()
                              if k in self['requires'])
            elif matches and matches.groupdict():
                pass
            else:
                return None
        if matches:
            params.update((k, v)
                          for k, v in matches.groupdict().items()
                          if v is not None)
        else:
            return None
        return RouteMatch(self, params)

    def assemble(self, **kwargs):
        """Converts the route into a path.

        Applies any keyword arguments as params on the route.

        Example:

        .. code-block:: python

            route = Route('search', path='/search/:keyword')
            route.assemble(keyword='test')  # /search/test
        """
        params = collections.ChainMap(kwargs or {}, self.get('defaults', {}))
        return ''.join(self.__build_path(self.segments, params))

    def __build_path(self, segments, params, optional=False):
        # Used to assemble a route
        path = []
        for segment in segments:
            is_optional = optional
            if not optional:
                is_optional = segment[0] == 'optional'
            if isinstance(segment[1], list):
                path.append(self.__build_path(segment[1], params, is_optional))
            else:
                value = segment[1]
                if segment[0] == 'param':
                    value = params.get(value)
                    if value:
                        path.append(str(value))
                    elif segment[1] not in self.get('requires', ()) or is_optional:
                        remove_segments = len(segments) - 1
                        path = path[0:-remove_segments]
                    else:
                        raise KeyError(
                            'Missing {0} in params.'.format(segment[1]))
                else:
                    path.append(segment[1])
        return ''.join(path)

    def __create_regex_from_segment_path(self, path, requires=None):
        """Converts a segemented path into a regular expression.

        Inspired by both Rails and ZF2.

        Args:
            path: the segmented path to convert to regex
            requires: a dict of required values for any optional segments

        Returns:
            SRE_Pattern for the segment
        """
        start, path_length, depth, segments = 0, len(path), 0, []
        depth_segments = [segments]
        pattern = re.compile('(?P<static>[^:\[\]]*)(?P<token>[:\[\]]|$)')
        token_pattern = re.compile('(?P<name>[^:/\[\]]+)')
        while start < path_length:
            matches = pattern.search(path, start)
            offset = '{0}{1}'.format(matches.groups()[0], matches.groups()[1])
            start += len(offset)
            token = matches.group('token')
            static_part = matches.group('static')
            if static_part:
                depth_segments[depth].append(('static', static_part))
            if token == ':':
                token_matches = token_pattern.search(path, start)
                param = token_matches.groupdict()['name']
                depth_segments[depth].append(('param', param))
                start += len(param)
            elif token == '[':
                depth += 1
                current_depth = depth - 1
                total_depths = len(depth_segments)
                if total_depths <= depth:
                    depth_segments.append([])
                depth_segments[current_depth].append(('optional', []))
                depth_segments[depth] = depth_segments[current_depth][
                    len(depth_segments[current_depth]) - 1][1]
            elif token == ']':
                del depth_segments[depth]
                depth -= 1
                if depth < 0:
                    raise ValueError('Bracket mismatch detected.')
            else:
                break
        del depth_segments
        return (
            re.compile(
                self.__convert_hierarchy_to_regex(segments, requires)), segments
        )

    def __convert_hierarchy_to_regex(self, hierarchy, requires):
        _regex = []
        for _type, value in hierarchy:
            if _type == 'static':
                _regex.append(re.escape(value))
            elif _type == 'optional':
                _regex.append(
                    '(?:{0})?'.format(self.__convert_hierarchy_to_regex(value, requires)))
            else:
                _regex.append(
                    '(?P<{0}>{1})'.format(value, requires.get(value, '[^/]+')))
        _regex.append('$')
        return ''.join(_regex)

    def __repr__(self):
        return (
            '<{0} name:{1} path:{2} match:{3}>'.format(
                get_qualified_name(self),
                self.name,
                self.path,
                self.regex.pattern)
        )
