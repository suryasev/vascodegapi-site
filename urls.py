from django.conf.urls.defaults import *
from django.conf import settings
from views import *

from django.views.generic.simple import direct_to_template

import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^gapi_demo/', include('gapi_demo.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^redirect_google_analytics/?$', 
      redirect_google_analytics),
    (r'^successful_connect_google_analytics/?$', 
      successful_connect_google_analytics),
    (r'^api_call/?$', api_call),
    (r'^download_file/?$', download_file),
    (r'^download_code/?$', download_code),
    (r'^/?$', direct_to_template, {'template': 'home.html'}),
    (r'^faq/?$', direct_to_template, {'template': 'faq.html'}),
    (r'^admin/(.*)', admin.site.root),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_HOME, 'site_media')})
)
