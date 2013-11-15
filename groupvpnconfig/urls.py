from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import configurationator.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'groupvpnconfig.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^configurations/', include(configurationator.views.urls)),
)
