from django.db import models

class Wiki(models.Model):
    wiki_url = models.CharField(max_length=200, unique=True)
    pb_create_time = models.IntegerField(null=True)
    pb_wikiname = models.CharField(max_length=200, null=True)
    pb_title = models.CharField(max_length=200, null=True)
    pb_about = models.CharField(max_length=200, null=True)
    pb_usercount = models.IntegerField(null=True)
    pb_pagecount = models.IntegerField(null=True)

    def __unicode__(self):
        return self.wiki_url


class Revisions(models.Model):
    wiki = models.ForeignKey(Wiki)
    page = models.CharField(max_length=200)
    rev_num = models.IntegerField()

    def __unicode__(self):
        return self.page + ' ' + str(self.rev_num)

    class Meta:
        unique_together = ("page", "rev_num")
