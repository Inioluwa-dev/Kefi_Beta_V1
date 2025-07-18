from django.shortcuts import render

def custom_404_view(request, exception=None, login_required=False):
    return render(request, '404.html', {'login_required': login_required}, status=404) 