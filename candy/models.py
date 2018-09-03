import datetime
from django.db import models
from django.utils import timezone
# Create your models here.
import json

class Token(models.Model):
    name = models.CharField(max_length=200)
    memo = models.CharField(max_length=2000)
    addr = models.CharField(max_length=512)
    type = models.IntegerField()
    active = models.BooleanField(default=True)
    create_time = models.DateTimeField('date published')

    def __str__(self):
        return json.dumps(self.as_dict(), default=str)

    def was_published_recently(self):
        return self.create_time >= timezone.now() - datetime.timedelta(days=1)

    def as_dict(self):
        attrs = self._meta.get_fields()
        return { "{}".format(attr.attname): getattr(self, attr.attname) for attr in attrs}