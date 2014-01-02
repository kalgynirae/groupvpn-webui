from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import ipaddress

from .models import Configuration, ConfigurationForm, LimitedConfigurationForm

def maybe_get_config(id, user):
    """Return the Configuration or cause Django to serve a 403 or 404."""
    c = get_object_or_404(Configuration, id=id)
    if c.owner == user:
        return c
    else:
        raise PermissionDenied

def list_configurations(request):
    configs = Configuration.objects.get(owner=request.user)
    context = {'configurations': configs}
    return render(request, 'groupvpn_webui/list_configurations.html', context)

def view_edit_configuration(request, id):
    c = maybe_get_config(id, request.user)
    context = {'configuration': c}
    return render(request, 'groupvpn_webui/view_edit_configuration.html',
                  context)

def download_configuration(request, id):
    c = maybe_get_config(id, request.user)
    zipped_configs, filename = c.get_zipped_configs()
    response = HttpResponse(zipped_configs, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def create_configuration(request):
    if request.user.is_authenticated():
        form_class = ConfigurationForm
    else:
        form_class = LimitedConfigurationForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            pass
    else:
        form = form_class()
    context = {'form': form, 'method': 'post'}
    return render(request, 'groupvpn_webui/create_configuration.html', context)
