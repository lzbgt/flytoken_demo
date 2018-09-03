import json
import uuid
from datetime import datetime
from hashids import Hashids
from django.db import models
# from django.utils import timezone
# from flytoken import settings
from django.contrib.auth.models import User,BaseUserManager
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from flytoken import settings

class UserManager(BaseUserManager):
    # def __init__(self, *args, **kwargs):
    #     super(UserManager, self).__init__(*args, **kwargs)

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save()
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save()
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    email = models.EmailField(unique=True)
    password = models.CharField(_('password'), max_length=128)
    is_active = models.BooleanField(default=False, verbose_name='account is activated')
    is_staff = models.BooleanField(default=False, verbose_name='admin')

    USERNAME_FIELD = 'email'

    # def __str__(self):
    #     return self.email
    #
    # def get_full_name(self):
    #     return self.email
    #
    # def get_short_name(self):
    #     return self.email



class Bonus(models.Model):
    t1 = models.DecimalField(default=0, max_digits=19, decimal_places=5, help_text="level 1 referrer")
    t2 = models.DecimalField(default=0, max_digits=19, decimal_places=5, help_text="level 2 referrer")
    t3 = models.DecimalField(default=0, max_digits=19, decimal_places=5, help_text="level 3 referrer")
    total_now = models.DecimalField(default=0, max_digits=19, decimal_places=5, help_text="current total bonus")
    limit = models.DecimalField(default=0, max_digits=19, decimal_places=5, help_text="limit of total bonus")
    last_update = models.DateTimeField('update time')

    def __str__(self):
        return json.dumps(self.as_dict(), default=str)

    def as_dict(self):
        attrs = self._meta.get_fields()
        return {"{}".format(attr.attname): getattr(self, attr.attname) for attr in attrs}


class AuditLog(models.Model):
    ufrom = models.IntegerField()
    uto = models.IntegerField()
    # 1表示第一级， #2表示第二级
    level = models.SmallIntegerField( default=0)
    coins = models.DecimalField(default=0, max_digits=19, decimal_places=5)
    created_time=models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = (('ufrom', 'uto'),)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vcode = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    #mobile = models.CharField(max_length=20, blank=True, unique=True)
    coins = models.DecimalField(default=0, max_digits=19, decimal_places=5)
    rcode = models.CharField(max_length=32, blank=True)
    last_update = models.DateTimeField('update time')

    def make_rcode(self):
        ids, hashids = self.get_referres(self.rcode)
        if ids is None:
            return hashids.encode(0, self.user.id)
        return hashids.encode(ids[1], self.user.id)

    @classmethod
    def get_referres(cls, rcode):
        hashids = Hashids(salt='flytoken')
        if rcode is None or rcode == '':
            return (None, hashids)
        ids = hashids.decode(rcode)
        if len(ids) != 2:
            return (None, hashids)
        for id in ids:
            if id != 0 and User.objects.get(id=id) == None:
                return (None, hashids)
        return (ids, hashids)

    @classmethod
    def create(cls, user, mobile, rcode):
        kwargs = {'user': user, 'rcode': rcode,
                   'coins': 0, 'last_update': timezone.now()}
        inst = cls(**kwargs)
        inst.save()

        return inst

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()