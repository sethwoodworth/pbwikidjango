from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    (r'^$', 'pbwikidjango.coding_tool.views.index'),
    (r'^wiki/(?P<wiki_url>\w+)$', 'pbwikidjango.coding_tool.views.view_wiki'),
    (r'^stats/(?P<wiki_url>\w+)$', 'pbwikidjango.coding_tool.views.stats'),
    (r'^post$', 'pbwikidjango.coding_tool.views.check'),
)
