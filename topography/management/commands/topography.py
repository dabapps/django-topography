from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
import inspect
import json
import sys


def trim(docstring):
    """https://www.python.org/dev/peps/pep-0257/#id18"""
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def inspect_method(name, method):
    return {
        'name': name,
        'docs': trim(method.__doc__),
        'lines': len(inspect.getsourcelines(method)[0])
    }


def inspect_methods(view_class):
    view = view_class()
    return [inspect_method(method_name, getattr(view, method_name.lower())) for method_name in view.allowed_methods if method_name != 'OPTIONS']


def extract_view_info_from_class(view_class):
    return {
        'name': view_class.__name__,
        'docs': trim(view_class.__doc__),
        'methods': inspect_methods(view_class)
    }


def extract_view_info(view):
    # Is this a CBV that "as_view" has been called on?
    if hasattr(view, 'cls'):
        return extract_view_info_from_class(view.cls)

    return {
        'name': view.__name__,
        'docs': trim(view.__doc__),
    }


def extract_url_data(urls, prefix=''):
    views = []
    for url in urls:
        if isinstance(url, RegexURLPattern):
            views.append({
                'view': extract_view_info(url.callback),
                'url': simplify_regex(prefix + url.regex.pattern)
            })
        if isinstance(url, RegexURLResolver):
            views += extract_url_data(url.url_patterns, prefix=simplify_regex(prefix + url.regex.pattern))
    return sorted(views, key=lambda view: view['url'])


class Command(BaseCommand):

    def handle(self, *args, **options):
        urls = __import__(settings.ROOT_URLCONF, {}, {}, ['']).urlpatterns
        self.stdout.write(json.dumps({
            "urls": extract_url_data(urls),
            "version": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }))
