# -*- coding: utf-8 -*-
from watson import framework
from watson.framework.debug import abc

TEMPLATE = """<style>
.watson-debug-toolbar__panel__framework__event {
    margin: 10px 0;
    font-size: 1.4em;
    color: #353535;
}
.watson-debug-toolbar__panel__framework table tr td:nth-of-type(2n) {
    width: 10%;
}
.watson-debug-toolbar__panel__framework table tr td:nth-of-type(3n) {
    width: 10%;
}
</style>
<div class="watson-debug-toolbar__panel__framework">
<dt>Version:</dt>
<dd>{{ version }}</dd>
<dt>Events</dt>
<dd>
{% for name, event in events|dictsort %}
<div class="watson-debug-toolbar__panel__framework__event">{{ name }}</div>
<table>
    <tr>
        <th>Callback</th><th>Priority</th><th>Triggered Once</th>
    </tr>
    {% for callback, priority, only_once in event %}
    <tr>
        <td>{{ callback|get_qualified_name }}</td><td>{{ priority }}</td><td>{{ only_once }}</td>
    </tr>
    {% endfor %}
</table>
{% endfor %}
</dd>
</div>
"""


class Panel(abc.Panel):
    title = 'Framework'

    def render(self):
        return self.renderer.env.from_string(TEMPLATE).render(
            version=framework.__version__,
            events=self.application.dispatcher.events)

    def render_key_stat(self):
        return 'v{0}'.format(framework.__version__)
