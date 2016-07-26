# -*- coding: utf-8 -*-
import collections
from pygments.formatters import HtmlFormatter
from watson.common import imports
from watson.framework import events

TEMPLATE = """<!-- Injected Watson Debug Toolbar -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.6.3/css/font-awesome.min.css" type="text/css" rel="stylesheet" />
<style type="text/css">
{{ pygment_styles }}
.watson-debug-toolbar__container {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    font-family: 'Open Sans', Helvetica, Arial, sans-serif;
    font-size: 12px;
    background: #fff;
    color: #7b7c7e;
}
.watson-debug-toolbar__buttons {
    background: #fefefe;
    border-bottom: 2px solid #d9dcdf;
    position: relative;
}
.watson-debug-toolbar__buttons a {
    color: inherit;
    text-decoration: none;
    padding: 10px 20px;
    display: inline-block;
    border-bottom: 2px solid transparent;
}
.watson-debug-toolbar__buttons a span {
    color: #aeabab;
    font-weight: bold;
    padding-left: 8px;
}
.watson-debug-toolbar__buttons a i {
    color: #aeabab;
    margin-right: 6px;
}
.watson-debug-toolbar__buttons a.active {
    background: #f8f8f9;
    border-color: #67bde3;
    color: #555;
}
.watson-debug-toolbar__container th {
    text-align: left;
}
.watson-debug-toolbar__container #DebugToolbarToggle {
    display: inline-block;
    background: #5e6a77;
    border-radius: 100%;
    color: #fff;
    padding-left: 7px;
    line-height: 0.9em;
    position: absolute;
    right: 10px;
    top: 8px;
    padding: 5px 7px 4px;
}
.watson-debug-toolbar__container #DebugToolbarToggle:hover {
    background: #353535;
}
.watson-debug-toolbar__panel {
    height: 200px;
    display: none;
    overflow: scroll;
    background: #f1f2f4;
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
    padding: 8px;
    border-right: 1px solid #9ea5ad;
    background: #5e6a77;
    color: #fefefe;
}
.watson-debug-toolbar__panel table td {
    font-family: inherit;
    background: #fff;
    padding: 4px 8px;
    border-right: 1px solid #f3f3f3;
}
.watson-debug-toolbar__panel table tr:nth-of-type(2n) td {
    background: #e3e6e9;
}
.watson-debug-toolbar__panel dt {
    font-weight: bold;
    font-size: 1.1em;
    float: left;
    width: 150px;
    clear: both;
    padding: 10px 16px;
    color: #383F47;
}
.watson-debug-toolbar__panel dd {
    color: inherit;
    margin-bottom: 4px;
    margin-left: 180px;
    padding: 10px;
}
.watson-debug-toolbar__resize {
    cursor: row-resize;
    height: 1px;
    background: #dadee1;
}
.codehilite .hll { background-color: #ffffcc }
.codehilite .c { color: #999988; font-style: italic } /* Comment */
.codehilite .err { color: #a61717; background-color: #e3d2d2 } /* Error */
.codehilite .k { color: #000000; font-weight: bold } /* Keyword */
.codehilite .o { color: #000000; font-weight: bold } /* Operator */
.codehilite .cm { color: #999988; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #999999; font-weight: bold; font-style: italic } /* Comment.Preproc */
.codehilite .c1 { color: #999988; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
.codehilite .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
.codehilite .ge { color: #000000; font-style: italic } /* Generic.Emph */
.codehilite .gr { color: #aa0000 } /* Generic.Error */
.codehilite .gh { color: #999999 } /* Generic.Heading */
.codehilite .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
.codehilite .go { color: #888888 } /* Generic.Output */
.codehilite .gp { color: #555555 } /* Generic.Prompt */
.codehilite .gs { font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #aaaaaa } /* Generic.Subheading */
.codehilite .gt { color: #aa0000 } /* Generic.Traceback */
.codehilite .kc { color: #000000; font-weight: bold } /* Keyword.Constant */
.codehilite .kd { color: #000000; font-weight: bold } /* Keyword.Declaration */
.codehilite .kn { color: #000000; font-weight: bold } /* Keyword.Namespace */
.codehilite .kp { color: #000000; font-weight: bold } /* Keyword.Pseudo */
.codehilite .kr { color: #000000; font-weight: bold } /* Keyword.Reserved */
.codehilite .kt { color: #445588; font-weight: bold } /* Keyword.Type */
.codehilite .m { color: #009999 } /* Literal.Number */
.codehilite .s { color: #d01040 } /* Literal.String */
.codehilite .na { color: #008080 } /* Name.Attribute */
.codehilite .nb { color: #0086B3 } /* Name.Builtin */
.codehilite .nc { color: #445588; font-weight: bold } /* Name.Class */
.codehilite .no { color: #008080 } /* Name.Constant */
.codehilite .nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
.codehilite .ni { color: #800080 } /* Name.Entity */
.codehilite .ne { color: #990000; font-weight: bold } /* Name.Exception */
.codehilite .nf { color: #990000; font-weight: bold } /* Name.Function */
.codehilite .nl { color: #990000; font-weight: bold } /* Name.Label */
.codehilite .nn { color: #555555 } /* Name.Namespace */
.codehilite .nt { color: #000080 } /* Name.Tag */
.codehilite .nv { color: #008080 } /* Name.Variable */
.codehilite .ow { color: #000000; font-weight: bold } /* Operator.Word */
.codehilite .w { color: #bbbbbb } /* Text.Whitespace */
.codehilite .mf { color: #009999 } /* Literal.Number.Float */
.codehilite .mh { color: #009999 } /* Literal.Number.Hex */
.codehilite .mi { color: #009999 } /* Literal.Number.Integer */
.codehilite .mo { color: #009999 } /* Literal.Number.Oct */
.codehilite .sb { color: #d01040 } /* Literal.String.Backtick */
.codehilite .sc { color: #d01040 } /* Literal.String.Char */
.codehilite .sd { color: #d01040 } /* Literal.String.Doc */
.codehilite .s2 { color: #d01040 } /* Literal.String.Double */
.codehilite .se { color: #d01040 } /* Literal.String.Escape */
.codehilite .sh { color: #d01040 } /* Literal.String.Heredoc */
.codehilite .si { color: #d01040 } /* Literal.String.Interpol */
.codehilite .sx { color: #d01040 } /* Literal.String.Other */
.codehilite .sr { color: #009926 } /* Literal.String.Regex */
.codehilite .s1 { color: #d01040 } /* Literal.String.Single */
.codehilite .ss { color: #990073 } /* Literal.String.Symbol */
.codehilite .bp { color: #999999 } /* Name.Builtin.Pseudo */
.codehilite .vc { color: #008080 } /* Name.Variable.Class */
.codehilite .vg { color: #008080 } /* Name.Variable.Global */
.codehilite .vi { color: #008080 } /* Name.Variable.Instance */
.codehilite .il { color: #009999 } /* Literal.Number.Integer.Long */
</style>
<div class="watson-debug-toolbar__container collapsed">
    <div class="watson-debug-toolbar__resize"></div>
    <div class="watson-debug-toolbar__inner">
        <div class="watson-debug-toolbar__buttons">
            <a href="javascript:;" id="DebugToolbarToggle">&times;</a>
            {% for module, panel in panels|dictsort %}
            <a href="javascript:;" data-panel="{{ panel.title }}"><i class="fa fa-{{ panel.icon }}" aria-hidden="true" title="{{ panel.title }}"></i> {{ panel.title }} <span class="watson-debug-toolbar__key-stat">{{ panel.render_key_stat() }}</span></a>
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
    var body = document.body,
        toolbar = document.querySelector('.watson-debug-toolbar__container'),
        toggle = document.getElementById('DebugToolbarToggle'),
        toolbarButtonContainer = toolbar.querySelector('.watson-debug-toolbar__buttons'),
        buttons = toolbar.querySelectorAll('.watson-debug-toolbar__buttons a:not([id])'),
        panels = toolbar.querySelectorAll('.watson-debug-toolbar__panel'),
        resizeHandle = toolbar.querySelector('.watson-debug-toolbar__resize'),
        panelOpen = false, resizingToolbar = false;
    body.style.paddingBottom = parseFloat(body.style.paddingBottom) + parseFloat(toolbar.offsetHeight);

    function removeActiveClasses() {
        var i;
        for (i = 0; i < panels.length; i++) {
            panels[i].classList.remove('active');
        }
        for (i = 0; i < buttons.length; i++) {
            buttons[i].classList.remove('active');
        }
    }
    toggle.addEventListener('click', function() {
        if (!panelOpen) {
            toolbar.parentNode.removeChild(toolbar);
            return;
        }
        if (toolbar.offsetHeight > 200) {
            toolbar.removeAttribute('style');
        }
        toolbar.classList.add('collapsed');
        removeActiveClasses();
        panelOpen = false;
    });
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            selectPanel(this);
        });
    }
    function selectPanel(button) {
        removeActiveClasses();
        toolbar.classList.remove('collapsed');
        button.classList.add('active');
        var panel = button.getAttribute('data-panel');
        toolbar.querySelector('.watson-debug-toolbar__panel[data-panel="'+panel+'"]').classList.add('active');
        panelOpen = true;
    }

    resizeHandle.addEventListener('mousedown', function() {
        resizingToolbar = true;
    });
    document.addEventListener('mousemove', function(evt) {
        if (resizingToolbar) {
            if (toolbar.classList.contains('collapsed')) {
                selectPanel(buttons[0]);
            }
            var height = (window.innerHeight - evt.clientY);
            if (height > toolbarButtonContainer.offsetHeight) {
                var newHeight = height + 'px';
                toolbar.style.height = newHeight;
                panels.forEach(function(n, i) {
                    n.style.height = height - 40 + 'px';
                });
            }
        }
        evt.stopPropagation();
        evt.preventDefault();
    });
    document.addEventListener('mouseup', function() {
        resizingToolbar = false;
    })
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
                self.panels[panel.title] = panel

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
                (self.renderer.env.from_string(TEMPLATE).render(
                    panels=self.panels), self.replace_tag))
            response.body = response.body.replace(self.replace_tag, html_body)
        return response
