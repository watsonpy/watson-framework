# -*- coding: utf-8 -*-
from datetime import datetime
from watson.framework.debug import abc
import logging

TEMPLATE = """<style>
.watson-debug-toolbar__panel__log table tr td:nth-of-type(1n) {
    width: 10%;
}
.watson-debug-toolbar__panel__log table tr td:nth-of-type(3n) {
    width: 2%;
}
.watson-debug-toolbar__panel__log table tr td:nth-of-type(4n) {
    width: 80%;
}
.watson-debug-toolbar__panel__log table tr td:nth-of-type(5n) {
    width: 1%;
}
</style>
<div class="watson-debug-toolbar__panel__log">
<table>
    <thead>
        <tr>
            <th>Time</th>
            <th>Name</th>
            <th>Level</th>
            <th>Message</th>
            <th>Line</th>
            <th>File</th>
        </tr>
    </thead>
    <tbody>
        {% for log in logs %}
        <tr>
            <td>{{ log.time|date(format='%Y-%m-%d %H:%M:%S') }}</td>
            <td>{{ log.name }}</td>
            <td>{{ log.levelname|title }}</td>
            <td>{{ log.getMessage() }}</td>
            <td>{{ log.lineno }}</td>
            <td>{{ log.pathname }}</td>
        </tr>
        {% else %}
        <tr>
            <td colspan="6">Nothing logged.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
</dd>
</div>
"""


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
        output = self.renderer.env.from_string(TEMPLATE).render(
            logs=debug_panel_handler.records)
        debug_panel_handler.clear()
        return output

    def render_key_stat(self):
        return '{0} messages'.format(len(debug_panel_handler.records))
