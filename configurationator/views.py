from django.conf.urls import patterns, url
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Configuration, ConfigurationForm

def list_configurations(request):
    pass

def edit_configuration(request, pk=None):
    instance = Configuration.objects.get(pk=pk) if pk else None
    if request.method == 'POST':
        form = ConfigurationForm(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = ConfigurationForm(instance=instance)
    return render(request, 'configuration.html', {'form': form})

def download_config_files(request):
    pass

urlpatterns = patterns('',
    url(r'^configurations/$', list_configurations, name='list'),
    url(r'^configurations/new$', edit_configuration, name='new'),
    url(r'^configurations/(\d{4})$', edit_configuration, name='edit'),
    url(r'^configurations/(\d{4}).tar.gz$', download_config_files,
        name='download'),
)
