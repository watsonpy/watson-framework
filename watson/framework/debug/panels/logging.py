# -*- coding: utf-8 -*-
from datetime import datetime
from watson.framework.debug import abc
import logging


class DebugPanelHandler(logging.Handler):
    _records = None

    @property
    def records(self):
        if not self._records:
            self._records = []
        return self._records

    def clear(self):
        self._records = []

    def emit(self, record):
        if not self.records:
            self.clear()
        setattr(record, 'time', datetime.fromtimestamp(record.created))
        self.records.append(record)


debug_panel_handler = DebugPanelHandler()
logging.root.addHandler(debug_panel_handler)


class Panel(abc.Panel):
    title = 'Logging'
    icon = 'list-ul'

    def render(self):
        output = self._render({
            'logs': debug_panel_handler.records
        })
        debug_panel_handler.clear()
        return output

    def render_key_stat(self):
        return '{0} messages'.format(len(debug_panel_handler.records))
