from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'groupvpn_webui.views.configure', name='configure'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration_email.backends.default.urls')),
)
