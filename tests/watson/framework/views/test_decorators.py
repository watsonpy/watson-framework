# -*- coding: utf-8 -*-
from watson.framework import views
from watson.framework.views.decorators import view


class MyController(object):
    @view(format='xml')
    def xml_action(self, *args, **kwargs):
        return {}

    @view(format='xml/text')
    def xml_full_mime_action(self):
        return {}

    @view(format='html', template='test')
    def html_action(self):
        return {}

    @view(format='json')
    def bool_action(self):
        return True


class TestViewDecorator(object):

    def test_view_model_format(self):
        controller = MyController()
        controller_response = controller.xml_action()
        assert isinstance(controller_response, views.Model)
        assert controller_response.format == 'xml'
        assert controller.xml_full_mime_action().format == 'xml/text'

    def test_view_model_template(self):
        controller = MyController()
        controller_response = controller.html_action()
        assert isinstance(controller_response, views.Model)
        assert controller_response.format == 'html'
        assert controller_response.template == 'test'

    def test_view_model_response(self):
        controller = MyController()
        controller_response = controller.bool_action()
        assert controller_response.data['content']
