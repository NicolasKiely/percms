from django import template
from django.core.urlresolvers import reverse

register = template.Library()

# Class string for box divs (bootstraptheming)
box_class = ' '.join([
    'col-lg-6', 'col-lg-offset-3',
    'col-md-6', 'col-md-offset-3',
    'content-box'
])

open_row_div_template = ''.join([
'<div class="container-fluid outer-content-box">',
'<div class="row">',
'<div class="{}">'
]) 

# Class string for half box divs
left_box_class = ' '.join([
    'col-lg-3', 'col-lg-offset-3',
    'col-md-3', 'col-md-offset-3',
    'col-sm-6', 'col-sm-offset-3',
    'content-box'
])

right_box_class = ' '.join([
    'col-lg-3', 'col-md-3', 'col-sm-6',
    'content-box'
])

form_open_template = '<form class="form-horizontal" action="{}" method="post">'
form_input_template = '<input class="form-control" type="{}" name="{}" value="{}">'
form_button = '<button type="submit" class="btn btn-primary pull-right">{}</button>'

open_row_div = open_row_div_template.format(box_class)
open_left_row_div = open_row_div_template.format(left_box_class)
open_right_row_div = open_row_div_template.format(right_box_class)
close_row_div = '</div></div></div>'


class Open_Box_Node(template.Node):
    def render(self, context):
        return open_row_div

class Open_Right_Box_Node(template.Node):
    def render(self, context):
        return open_right_row_div

class Open_Left_Box_Node(template.Node):
    def render(self, context):
        return open_left_row_div

class Close_Box_Node(template.Node):
    def render(self, context):
        return close_row_div

@register.tag(name='open_box')
def do_open_box(parse, token):
    return Open_Box_Node()

@register.tag(name='left_box')
def do_open_left_box(parse, token):
    return Open_Left_Box_Node()

@register.tag(name='right_box')
def do_open_right_box(parse, token):
    return Open_Right_Box_Node()

@register.tag(name='close_box')
def do_close_box(parse, token):
    return Close_Box_Node()

@register.filter(name='common_form')
def do_common_text_input(form):
    ''' Filter for auto-generating form from dict '''
    action = form.get('action', '')
    csrf = form.get('csrf', '')
    form_str = form_open_template.format(reverse(action)) + '<div class="form-group">'
    for field in form['fields']:
        label = field.get('label', '')
        ftype = field.get('type', 'text')
        value = field.get('value', '')
        name = field.get('name', label)
        form_str += build_input_string(label, ftype, value, name)

    form_str += build_input_string('', 'hidden', csrf, 'csrfmiddlewaretoken')
    button_text = form.get('button', 'Submit')
    return form_str +'</div>'+ form_button.format(button_text) +'</form>'

def build_input_string(label, ftype, value, name):
    input_str = ''
    if ftype == 'hidden':
        input_str += form_input_template.format("hidden", name, value)
    else:
        input_str += '<label class="col-sm-3 control-label">'+ label +'</label>'
        input_str += '<div class="col-sm-8">'
        input_str += form_input_template.format(ftype, name, value)
        input_str += '</div>'
    return input_str
