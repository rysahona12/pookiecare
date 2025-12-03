from django.shortcuts import render


def review_page(request):
    """
    Renders the main review page template.
    """
   
    return render(request, 'index.html', {})