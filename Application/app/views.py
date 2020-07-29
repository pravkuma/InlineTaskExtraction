"""
Definition of views.
"""
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.template import RequestContext
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .nlp import TaskExtractor
from datetime import datetime

# Whenever the django is setting up the server, it will construct the task_extractor here so that all
# the required information remains in the main memory for faster outputs.
task_extractor = TaskExtractor()

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

@api_view(['GET', 'POST'])
def extract_task(request):
    """API endpoint where task extraction requests are landed"""
    if request.method == 'POST':
        if (request and request.data and request.data['text']):
            text = request.data['text']

            task = task_extractor.getTask(text)
        
            return JsonResponse(task, safe=False)
        else:
            return JsonResponse({'error': 'Invalid input'})

    elif request.method == 'GET':
        return JsonResponse({'error': 'Please enter some valid text and make a post request. Format ==> {"text": "value"}'})