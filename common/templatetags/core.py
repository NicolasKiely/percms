from django import template

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
