# -*- coding: utf-8 -*-
from watson.mail import Message


class Mailer(object):
    backend = None
    renderer = None

    def __init__(self, backend, renderer):
        self.backend = backend
        self.renderer = renderer

    def send(
            self,
            template=None,
            alternative_template=None,
            body=None,
            **kwargs):
        kwargs['body'] = body
        if template:
            kwargs['body'] = self.renderer.render(template, data=body)
        if alternative_template:
            kwargs['alternative'] = self.renderer.render(
                alternative_template, data=body)
        message = Message(
            backend=self.backend,
            **kwargs)
        return message.send()
