# -*- coding: utf-8 -*-
from watson.mail import Message


class Mailer(object):
    backend = None
    renderer = None

    def __init__(self, backend, renderer):
        self.backend = backend
        self.renderer = renderer

    def send(self, template=None, body=None, **kwargs):
        if template:
            body = self.renderer.render(template, data=body)
        message = Message(
            backend=self.backend,
            body=body,
            **kwargs)
        return message.send()
