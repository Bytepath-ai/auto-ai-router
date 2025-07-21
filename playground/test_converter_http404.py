"""Test to demonstrate Http404 raised in path converters not being caught properly."""
import os
import sys
import django
from django.conf import settings
from django.urls import path
from django.http import Http404, HttpResponse
from django.test import RequestFactory
from django.core.handlers.exception import response_for_exception

# Configure Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='test',
    ROOT_URLCONF=__name__,
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
    MIDDLEWARE=[],
)

django.setup()

# Custom converter that raises Http404
class CustomConverter:
    regex = r'[^/]+'
    
    def to_python(self, value):
        if value == 'invalid':
            raise Http404("Invalid value in converter")
        return value
    
    def to_url(self, value):
        return str(value)

# Register the converter
from django.urls.converters import register_converter
register_converter(CustomConverter, 'custom')

# Define a view
def test_view(request, value):
    return HttpResponse(f"Value: {value}")

# Define URL patterns
urlpatterns = [
    path('test/<custom:value>/', test_view, name='test'),
]

# Test the behavior
def test_converter_http404():
    print("Testing Http404 raised in path converter...")
    
    # Create a request
    factory = RequestFactory()
    request = factory.get('/test/invalid/')
    
    # Try to resolve the URL
    from django.urls import resolve, Resolver404
    
    try:
        match = resolve('/test/invalid/')
        print(f"Resolution succeeded (unexpected): {match}")
    except Http404 as e:
        print(f"Http404 raised (expected): {e}")
        # This is what happens - Http404 is raised but not caught properly
        # by the exception handling system
        
        # Let's see what response_for_exception returns
        response = response_for_exception(request, e)
        print(f"Response status: {response.status_code}")
        print(f"Response type: {type(response)}")
        
        # Check if it's a technical 404 response
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'URLconf' in content:
                print("Got technical 404 response (good)")
            else:
                print("Got generic 404 response (bad)")
    except Resolver404 as e:
        print(f"Resolver404 raised: {e}")
    except ValueError as e:
        print(f"ValueError raised: {e}")
    except Exception as e:
        print(f"Other exception raised: {type(e).__name__}: {e}")

if __name__ == '__main__':
    test_converter_http404()