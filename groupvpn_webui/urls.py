from django.conf.urls import patterns, url

urlpatterns = patterns('groupvpn_webui.views',
    url(r'^$', 'list_configurations', name='list_configurations'),
    url(r'^new/$', 'create_configuration', name='create_configuration'),
    url(r'^(\d+)/$', 'view_edit_configuration',
        name='view_edit_configuration'),
    url(r'^(\d+)/download/$', 'download_configuration',
        name='download_configuration'),
)
