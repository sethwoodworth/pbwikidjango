from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^code/', include('pbwikidjango.coding_tool.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Serves images and css
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'static'}),
)
