# -*- coding: utf-8 -*-
from pytest import raises
from watson.framework.i18n import translate


class TestTranslator(object):

    def test_repr(self):
        translator = translate.Translator(
            default_locale='en',
            package='tests.watson.framework.i18n.locales')
        assert repr(translator) == '<watson.framework.i18n.translate.Translator current:en locales:0>'

    def test_translate_string(self):
        translator = translate.Translator(
            default_locale='en',
            package='tests.watson.framework.i18n.locales')
        assert translator.translate('test.string') == 'This is a sample string'
        assert repr(translator) == '<watson.framework.i18n.translate.Translator current:en locales:1>'

    def test_translate_missing_string(self):
        translator = translate.Translator(
            default_locale='en',
            package='tests.watson.framework.i18n.locales')
        with raises(translate.TranslatorError):
            translator.translate('missing.string')

    def test_translate_formatted_string(self):
        translator = translate.Translator(
            default_locale='en',
            package='tests.watson.framework.i18n.locales')
        assert translator.translate('test.string.formatted', type='formatted') == 'This is a formatted string'

    def test_translate_fallback_string(self):
        translator = translate.Translator(
            default_locale='en',
            package='tests.watson.framework.i18n.locales',
            fallback_locale='fallback')
        assert translator.translate('test.fallback') == 'A fallback string'
