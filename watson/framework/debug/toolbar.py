# -*- coding: utf-8 -*-
import collections
from watson.common import imports
from watson.framework import events

TEMPLATE = """<!-- Injected Watson Debug Toolbar -->
<style type="text/css">
.watson-debug-toolbar__container {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    font-family: Helvetica, Arial, sans-serif;
    font-size: 12px;
    background: #fff;
    color: #7b7c7e;
    border-top: 1px solid #c3c3c3;
}
.watson-debug-toolbar__buttons {
    background: #f2f2f2;
    padding: 8px;
    border-bottom: 1px solid #c3c3c3;
    position: relative;
}
.watson-debug-toolbar__buttons a {
    color: inherit;
    text-decoration: none;
    padding: 4px 8px;
    display: inline-block;
    border-radius: 4px;
}
.watson-debug-toolbar__buttons a span {
    color: #aeabab;
    font-weight: bold;
    padding-left: 8px;
}
.watson-debug-toolbar__buttons a.active {
    background: #dcdcdc;
    border-color: #c4c4c4;
    color: #555;
}
.watson-debug-toolbar__container th {
    text-align: left;
}
.watson-debug-toolbar__container #DebugToolbarToggle {
    display: inline-block;
    height: 12px;
    width: 5px;
    background: #7b7c7e;
    border-radius: 14px;
    color: #fff;
    padding-left: 7px;
    line-height: 0.9em;
    position: absolute;
    right: 10px;
    top: 8px;
}
.watson-debug-toolbar__container #DebugToolbarToggle:hover {
    background: #353535;
}

.watson-debug-toolbar__panel {
    height: 200px;
    display: none;
    overflow: scroll;
}
.watson-debug-toolbar__container.collapsed .watson-debug-toolbar__panel {
    display: none;
}
.watson-debug-toolbar__container .watson-debug-toolbar__panel.active {
    display: block;
}
.watson-debug-toolbar__panel table {
    width: 100%;
    border-spacing: 0;
    border-collapse: collapse;
    font-size: inherit;
}
.watson-debug-toolbar__panel table th {
    padding: 8px 4px;
    border-right: 1px solid #f1f1f1;
    background: #7b7c7e;
    color: #cccbcb;
}
.watson-debug-toolbar__panel table td {
    font-family: inherit;
    background: #fff;
    padding: 4px;
    border-right: 1px solid #f3f3f3;
}
.watson-debug-toolbar__panel table tr:nth-of-type(2n) td {
    background: #f7f7f7;
}
.watson-debug-toolbar__panel dt {
    font-weight: bold;
    font-size: 1.1em;
    float: left;
    width: 160px;
    clear: both;
    padding: 4px 6px;
    color: #353535;
}
.watson-debug-toolbar__panel dd {
    color: inherit;
    margin-bottom: 4px;
    margin-left: 160px;
    padding: 4px 6px;
}
</style>
<div class="watson-debug-toolbar__container collapsed">
    <div class="watson-debug-toolbar__inner">
        <div class="watson-debug-toolbar__buttons">
            <a href="javascript:;" id="DebugToolbarToggle">x</a>
            {% for module, panel in panels|dictsort %}
            <a href="javascript:;" data-panel="{{ panel.title }}">{{ panel.title }} <span class="watson-debug-toolbar__key-stat">{{ panel.render_key_stat() }}</span></a>
            {% endfor %}
        </div>
        {% for module, panel in panels|dictsort %}
        <div class="watson-debug-toolbar__panel" data-panel="{{ panel.title }}">
        {{ panel }}
        </div>
        {% endfor %}
    </div>
</div>
<script type="text/javascript">
    function removeClass(el, className) {
        className = ' ' + className;
        el.className = el.className.replace(className, '');
    }
    function addClass(el, className) {
        removeClass(el, className);
        el.className += ' ' + className;
    }
    var body = document.body,
        toolbar = document.querySelector('.watson-debug-toolbar__container'),
        toggle = document.getElementById('DebugToolbarToggle'),
        buttons = toolbar.querySelectorAll('.watson-debug-toolbar__buttons a:not([id])'),
        panels = toolbar.querySelectorAll('.watson-debug-toolbar__panel'),
        panelOpen = false;
    body.style.paddingBottom = parseFloat(body.style.paddingBottom) + parseFloat(toolbar.offsetHeight);

    function removeActiveClasses() {
        var i;
        for (i = 0; i < panels.length; i++) {
            removeClass(panels[i], 'active');
        }
        for (i = 0; i < buttons.length; i++) {
            removeClass(buttons[i], 'active');
        }
    }
    toggle.addEventListener('click', function() {
        if (!panelOpen) {
            toolbar.parentNode.removeChild(toolbar);
            return;
        }
        removeActiveClasses();
        panelOpen = false;
    });
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            removeActiveClasses();
            removeClass(toolbar, 'collapsed');
            addClass(this, 'active');
            var panel = this.getAttribute('data-panel');
            addClass(toolbar.querySelector('.watson-debug-toolbar__panel[data-panel="'+panel+'"]'), 'active');
            panelOpen = true;
        });
    }
</script>
"""


class Toolbar(object):
    config = None
    panels = None
    replace_tag = '</body>'

    def __init__(self, config, application, renderer):
        """Application can be any WSGI callable
        """
        self.application = application
        self.config = config
        self.renderer = renderer
        self.panels = collections.OrderedDict()
        for module, settings in config['panels'].items():
            if settings['enabled']:
                panel = imports.load_definition_from_string(
                    module)(settings, renderer, application)
                panel.register_listeners()
                self.panels[module] = panel

    def register_listeners(self):
        self.application.dispatcher.add(events.RENDER_VIEW, self.render, -1000)

    def render(self, event):
        """Render the toolbar to the browser.
        """
        for module, panel in self.panels.items():
            panel.event = event
        context = event.params['context']
        response, view_model = context['response'], event.params['view_model']
        if view_model.format == 'html':
            html_body = ''.join(
                (self.renderer.env.from_string(TEMPLATE).render(panels=self.panels), self.replace_tag))
            response.body = response.body.replace(self.replace_tag, html_body)
        return response
