from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response

from urllib import urlopen, urlencode

from pbwikidjango.coding_tool.models import Revisions, Wiki

class PBwiki(object):
    def __init__(self, url):
        # Define url for everythign later
        self.url = url

    def api_call(self, op, **kwargs):
        # make a call
        # op is pbwiki operator
        # kwargs are kv options for ops
        kwargs['_type'] = 'jsontext' # always return json
        url_args = '/'.join(["%s/%s" % (k,v) for k, v in kwargs.iteritems()])
        call_url = '%s/api_v2/op/%s/%s' % (self.url, op, url_args)
        print call_url

        resp = urlopen(call_url)
        json = '\n'.join(resp.read().split('\n')[1:-2])
        resp.close()
        print 'url fetched, closed'

        # translate json into py dict
        json_translation_table = {'true': True, 'false': False, 'null': None}
        return eval(json, json_translation_table, {})  



def index(request):
    return render_to_response('coding_tool/index.html', {'msg': 'Welcome, to ...'})

def view_wiki(request, wiki_url):
    # TODO: add checks and handling for wiki url (trailing /) (.com)
    url = 'http://' + wiki_url + '.pbworks.com'
    print url
    api = PBwiki(url)
    pb_pages = api.api_call('GetPages')
    page_list = []
    for page in pb_pages['pages']:
        page_list.append(page['name'])
    revisions = {} 
    for page in page_list:
        kwarg = {'page': page}
        p_revs = api.api_call('GetPageRevisions', **kwarg)['revisions']
        revisions[page] = p_revs

    return render_to_response('coding_tool/frame.html', {'revisions': revisions, 'pages': page_list})
