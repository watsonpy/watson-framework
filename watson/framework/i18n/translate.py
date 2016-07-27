# -*- coding: utf-8 -*-
from watson.common import imports
from watson.framework import exceptions


class Translator(object):

    """Provide localize support for Watson projects.

    Localization files are standard Python modules, with a single dictionary
    within them named `strings`. The Translator can also be used as a simple
    way to manage string files.

    Example:

    .. code-block:: python

        # project/locales/en.py
        strings = {
            'my.string': 'My translated string'
        }

        # controller.py
        translator = Translator(default_locale='en', package='project.locales')
        translator.translate('my.string')  # My translated string

    Attributes:
        current_locale (string): The current locale to use when translating.
                                 Can be override in the translate() method.
    """

    current_locale = None

    _locales = None
    _package = None
    _fallback_locale = None
    _shared_instance = None

    def __init__(self, default_locale, package, fallback_locale=None):
        """Initialize the translator.

        Args:
            default_locale (string): The default locale to use
            package (string): The python package to search for locale files
            fallback_locale (string): The fallback locale to use if the string
                                      is not found within the requested locale
        """
        self._locales = {}
        self._package = package
        self._fallback_locale = fallback_locale if fallback_locale else default_locale
        self.current_locale = default_locale
        Translator._shared_instance = self

    def load_locale(self, locale):
        """Load a locale file into the translator.

        Args:
            locale (string): The locale module to attempt to load
        """
        locale_package = '{}.{}'.format(self._package, locale)
        locale_strings = imports.import_module(locale_package)
        self._locales[locale] = getattr(locale_strings, 'strings')

    def remove_locale(self, locale):
        """Remove the specified locale.

        Args:
            locale (string): The locale module to remove
        """
        del self._locales[locale]

    def translate(self, string, locale=None, **kwargs):
        """Retrieve a string to be translated from the relevant locale.

        Any additional kwargs are sent through to be formatted.

        Args:
            string (string): The string to localize
            locale (string): Override the default locale if required

        Raises:
            TranslatorError if string is not found in the locale or the
            fallback locale files.

        Returns:
            The requested string value
        """
        locale = locale if locale else self.current_locale
        if locale not in self._locales:
            self.load_locale(locale)
        try:
            localized_string = self._locales[locale][string]
            return localized_string.format(**kwargs)
        except KeyError:
            if locale is not self._fallback_locale:
                return self.translate(string, self._fallback_locale, **kwargs)
            raise TranslatorError(message='"{0}" not found in locale "{1}"'.format(
                string, locale))

    def __repr__(self):
        return '<{0} current:{1} locales:{2}>'.format(
            imports.get_qualified_name(self),
            self.current_locale,
            len(self._locales))


def translate(string, locale=None, **kwargs):
    """Convenience method for the translator.

    Assumes the translator has already been initialized in the project.
    See watson.framework.support.jinja2.globals for a way to utilize this in
    the view.

    Args:
        string (string): The string to find
        locale (string): Override the default locale if required

    Example:

    .. code-block:: python

        from watson.framework.i18n.translate import translate as _
        print(_('my.string'))
    """
    return Translator._shared_instance.translate(
        string, locale=locale, **kwargs)


class TranslatorError(exceptions.ApplicationError):

    """Error to be raised when a key is missing from the locale.
    """
