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

    # query db then api for wiki info, stored, used in stats below
    wiki = Wiki.objects.filter(wiki_url=wiki_url).all()
    if not wiki:
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
    pb_pages = api.api_call('GetPages')
    page_list = []
    for page in pb_pages['pages']:
        page_list.append(page['name'])
    revisions = {} 
    for page in page_list:
        kwarg = {'page': page}
        p_revs = api.api_call('GetPageRevisions', **kwarg)['revisions']
        revisions[page] = p_revs
    create = ''
    for k in revisions:
        for r in revisions[k]:
            if r < create:
                create = r
    revs = Revisions.objects.filter(wiki__pb_wikiname=wiki_url).all()

    return render_to_response('coding_tool/frame.html', {'wiki_title': wiki_url ,'wiki_creation': create, 'wiki_url': url, 'revisions': revisions, 'pages': page_list, 'revs': revs})

def stats(request, wiki_url):
    url = 'http://' + wiki_url + '.pbworks.com'
    print url
    api = PBwiki(url)

    wiki = Wiki.objects.filter(wiki_url=wiki_url).all()
    if not wiki:

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

    rev_list = Revisions.objects.filter(wiki__pb_wikiname=wiki_url).all()
    if not rev_list:
        pb_pages = api.api_call('GetPages')
        page_list = []
        for page in pb_pages['pages']:
            page_list.append(page['name'])

        rev_list = {} 
        for page in page_list:
            kwarg = {'page': page}
            p_revs = api.api_call('GetPageRevisions', **kwarg)['revisions']
            rev_list[page] = p_revs

            for rev in p_revs:
                print rev
                # store revision info(s)
                rev = Revisions(wiki=wiki[0], page=page, rev_num=rev )
                rev.save()

    else:
        # TODO: make this much much better later
        pass_d = {}
        for x in rev_list:
            pass_d[x.page] = []
        for x in rev_list:
            pass_d[x.page].append(x.rev_num)
        rev_list = pass_d

    return render_to_response('coding_tool/stats.html', {'wiki': wiki, 'revisions': rev_list})
