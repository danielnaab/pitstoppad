from django import template

register = template.Library()

@register.filter('modulo')
def modulo(value, arg):
    if value % arg == 0:
        return True
    else: 
        return False

@register.filter('replace')
def replace(value, args):
    args = args.split(',')
    if len(args) !=2:
        raise Exception, 'replace filter requires two parameters of form: "arg1,arg2"'
    
    return value.replace(args[0], args[1])
