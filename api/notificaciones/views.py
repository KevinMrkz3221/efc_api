from django.shortcuts import render

# Create your views here.

def healthcheck(request):
    """
    Health check endpoint to verify if the API is running.
    """
    return render(request, {'health': 'OK'}, status=200)