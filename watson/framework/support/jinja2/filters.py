# -*- coding: utf-8 -*-
# Filter functions for Jinja2 templates
from urllib import parse
from watson.common import imports


def get_qualified_name(obj):
    """Retrieve the qualified class name of an object.
    """
    return imports.get_qualified_name(obj)


def label(obj):
    """Render a form field with the label attached.
    """
    return obj.render_with_label()


def merge_query_string(obj, values):
    """Merges an existing dict of query string values and updates the values.

    Args:
        obj: The original dict
        values: The new query string values

    Example:

    .. code-block:: python

        # assuming ?page=2
        request().get|merge_query_string({'page': 1})  # ?page=1
    """
    qs_parts = dict(obj)
    qs_parts.update(values)
    return '?{0}'.format(parse.urlencode(qs_parts))
