from django.db import models

class Wiki(models.Model):
    wiki_url = models.CharField(max_length=200)
    pb_create_time = models.DateField(null=True)
    pb_wikiname = models.CharField(max_length=200, null=True)
    pb_title = models.CharField(max_length=200, null=True)
    pb_about = models.CharField(max_length=200, null=True)
    pb_usercount = models.IntegerField(null=True)
    pb_pagecount = models.IntegerField(null=True)


class Revisions(models.Model):
    wiki = models.ForeignKey(Wiki)
    page = models.CharField(max_length=200)
    revision = models.IntegerField()
