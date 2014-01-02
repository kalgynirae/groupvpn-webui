from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', RedirectView.as_view(url='/config/')),
    url(r'^config/', include('groupvpn_webui.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('registration_email.backends.default.urls')),
)
