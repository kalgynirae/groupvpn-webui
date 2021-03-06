import subprocess

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import ipaddress

from .forms import ConfigurationForm, LimitedConfigurationForm
from .models import Configuration
from .settings import get_setting

def maybe_get_config(id, user):
    """Return the Configuration or cause Django to serve a 403 or 404."""
    c = get_object_or_404(Configuration, pk=id)
    if c.owner and c.owner != user:
        raise PermissionDenied
    else:
        return c

def list_configurations(request):
    configs = Configuration.objects.filter(owner__exact=request.user.pk)
    context = {'configurations': configs}
    return render(request, 'groupvpn_webui/list_configurations.html', context)

def view_edit_configuration(request, id):
    c = maybe_get_config(id, request.user)

    if request.user.is_authenticated():
        form_class = ConfigurationForm
    else:
        form_class = LimitedConfigurationForm

    if request.method == 'POST':
        form = form_class(request.POST, instance=c)
        if form.is_valid():
            if request.user.is_authenticated():
                form.instance.owner = request.user
            form.save()
            return redirect(form.instance)
    else:
        form = form_class(instance=c)

    # We want the group_name to be read-only simply because changing the
    # group_name is confusing to the average user. It could still be changed by
    # submitting a faulty form, but that's not a problem.
    form.fields['group_name'].widget.attrs['readonly'] = True
    context = {'configuration': c, 'form': form, 'method': 'post',
               'filename': c.group_name + '.zip'}
    return render(request, 'groupvpn_webui/view_edit_configuration.html',
                  context)

def download_configuration(request, id):
    c = maybe_get_config(id, request.user)
    filename = c.group_name + '.zip'
    # Make a copy (slice of all elements) so we don't modify the original
    args = get_setting('GROUPVPN_CONFIG_ARGS')[:]
    args.extend([
        c.group_name.encode('utf-8'),
        get_setting('GROUPVPN_XMPP_HOST'),
        str(c.machine_count),
        '--ip-network',
        str(c.ip_network),
        '--seed',
        c.random_seed.encode('utf-8')])
    if not c.encryption:
        args.append('--no-encryption')
    zipped_configs = subprocess.check_output(args)
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
            if request.user.is_authenticated():
                form.instance.owner = request.user
            form.save()
            return redirect(form.instance)
    else:
        form = form_class()
    context = {'form': form, 'method': 'post'}
    return render(request, 'groupvpn_webui/create_configuration.html', context)
