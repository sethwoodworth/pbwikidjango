from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext            

from urllib import urlopen, urlencode
import datetime

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

@csrf_protect
def view_wiki(request, wiki_url):
    # Initial wiki load via ./wiki/$wiki_name
    # TODO: add checks and handling for wiki url (trailing /) (.com)
    url = 'http://' + wiki_url + '.pbworks.com'
    api = PBwiki(url)
    print "FLOW CONTROL"
    print url

    # query db then api for wiki info, stored, used in stats below
    wiki = Wiki.objects.filter(wiki_url=wiki_url).all()
    print str(wiki) + "wiki object from db!!!!"
    
    if not wiki:
        print "wiki didn't return properly or not found in db, fetching"
        wiki_info = api.api_call('GetWikiInfo')
        # Store wiki info
        wiki = Wiki()
        wiki.wiki_url = wiki_url
        wiki.pb_create_time = wiki_info['create_time']
        wiki.pb_wikiname = wiki_info['wikiname']
        wiki.pb_title = wiki_info['title']
        wiki.pb_about = wiki_info['about']
        wiki.pb_usercount = wiki_info['usercount']
        wiki.pb_pagecount = wiki_info['pagecount']
        wiki.save() 
    else:
        print "the db looks FINE, IT's FINE"

    # do we have revisions?
    try:
        one_wiki = wiki[0]
        rs = Revisions.objects.filter(wiki = one_wiki.pk).all()
    except:
        rs = False
    # or do the rev foreignkey like this:
    # revs = Revisions.objects.filter(wiki__pb_wikiname=wiki_url).all()
    print "LETS GET REVISIONS, YAYYYY"
    print rs

    # Either loop over returned db or call via api and store in revisions dict
    revisions = {} 
    if not rs:
        # "BOO, my revisions suck. let's get some better ones"
        pb_pages = api.api_call('GetPages')
        page_list = []

        for page in pb_pages['pages']:
            page_list.append(page['name'])
        for page in page_list:
            kwarg = {'page': page}
            p_revs = api.api_call('GetPageRevisions', **kwarg)['revisions']
            revisions[page] = p_revs
            # save this to the DB while we have it
            for rev in p_revs:
                rev = Revisions()
                rev.wiki = wiki
                rev.page = page
                rev.rev_num = rev
    else:
        for i in rs.values():
            revisions[str(i['page'])] = []
        page_list = revisions
        for i in revisions:
            for j in rs.values():
                if j['page'] == i:
                    revisions[i].append(j['rev_num'])


    # embarassing, but before we send to page, reformat as a datetime object FOR REAL
    # TODO: change the db to allow for datetime objects instead of INT()
    return render_to_response('coding_tool/frame.html', {'wiki_title': wiki_url ,'wiki_creation': datetime.datetime.fromtimestamp(wiki[0].pb_create_time), 'wiki_url': url, 'revisions': revisions, 'pages': page_list}, context_instance=RequestContext(request))

def stats(request, wiki_url):
    url = 'http://' + wiki_url + '.pbworks.com'
    print url
    api = PBwiki(url)

    wiki = Wiki.objects.filter(wiki_url=wiki_url).all()
    if wiki:
        rev_list = Revisions.objects.filter(wiki__pb_wikiname=wiki_url).all()

        wiki[0].pb_create_time = datetime.datetime.fromtimestamp(wiki[0].pb_create_time)

        revisions = {}
        for i in rev_list.values():
            revisions[str(i['page'])] = []
        page_list = revisions
        for i in revisions:
            for j in rev_list.values():
                if j['page'] == i:
                    revisions[i].append(j['rev_num'])
        return render_to_response('coding_tool/stats.html', {'wiki': wiki[0], 'revisions': revisions })
    else:
        return render_to_response('coding_tool/stats.html', {'wiki': 'wiki', 'revisions': 'rev_list'})
        




@csrf_protect
def check(request):
    print "got a request from check()"
    if request.POST.get('wiki_url'):
        print request.POST.get('wiki_url')
        wiki_url = request.POST.get('wiki_url')
        if wiki_url[:7] == 'http://':
            wiki_url = wiki_url[7:]
        subdomain = wiki_url.split('.')[0]
        return view_wiki(request, subdomain)
