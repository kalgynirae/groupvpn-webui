from django.http import HttpResponse
from django.shortcuts import render
import ipaddress

from .models import ConfigurationForm, LimitedConfigurationForm

def configure(request):
    if request.user.is_authenticated():
        form_class = ConfigurationForm
    else:
        form_class = LimitedConfigurationForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            zipped_configs, filename = form.instance.get_zipped_configs()
            response = HttpResponse(zipped_configs,
                                    content_type='application/zip')
            response['Content-Disposition'] = ('attachment; filename=%s'
                                               '' % filename)
            return response
    else:
        form = form_class()
    context = {'form': form, 'method': 'post'}
    return render(request, 'groupvpn_webui/configuration.html', context)
