# -*- coding: utf-8 -*-
# Namespaced packages, see http://www.python.org/dev/peps/pep-0420/

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:  # pragma: no cover
    from pkgutil import extend_path  # pragma: no cover
    __path__ = extend_path(__path__, __name__)  # pragma: no cover
