from django import template

from log.forms import *

register = template.Library()

@register.inclusion_tag('include/html_helpers/corner_box_top.html')
def corner_box_top(classes=''):
    return {'classes': classes}

@register.inclusion_tag('include/html_helpers/corner_box_bottom.html')
def corner_box_bottom(classes=''):
    return {'classes': classes}

@register.inclusion_tag('include/html_helpers/info_box_top.html')
def info_box_top(classes=''):
    return {'classes': classes}

@register.inclusion_tag('include/html_helpers/info_box_bottom.html')
def info_box_bottom(classes=''):
    return {'classes': classes}

@register.inclusion_tag('include/html_helpers/info_box2_top.html')
def info_box2_top(classes=''):
    return {'classes': classes}

@register.inclusion_tag('include/html_helpers/info_box2_bottom.html')
def info_box2_bottom(classes=''):
    return {'classes': classes}

@register.inclusion_tag('include/html_helpers/form_submit_handler.html')
def form_submit_handler(form, id, post_url):
    return {'form': form,
            'id': id,
            'post_url': post_url,
            }

@register.inclusion_tag('include/html_helpers/formhandler_head.html')
def formhandler_head(form_handler, extra_handler=None):
    return {'form_handler': form_handler, 'extra_handler': extra_handler}

class SplitListNode(template.Node):
    def __init__(self, results, cols, new_results):
        self.results, self.cols, self.new_results = results, cols, new_results

    def split_seq(self, results, cols=2):
        start = 0
        for i in xrange(cols):
            stop = start + len(results[i::cols])
            yield results[start:stop]
            start = stop

    def render(self, context):
        context[self.new_results] = self.split_seq(context[self.results], int(self.cols))
        return ''

@register.tag
def list_to_columns(parser, token):
    """Parse template tag: {% list_to_colums results as new_results 2 %}"""
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "list_to_columns results as new_results 2"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "second argument to the list_to_columns tag must be 'as'"
    return SplitListNode(bits[1], bits[4], bits[3])
