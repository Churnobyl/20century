from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import os
from uuid import uuid4
from datetime import date

# 프로필 파일 이름 uuid형식으로 바꾸기
def rename_imagefile_to_uuid(instance, filename):
    now = date.today()
    upload_to = f'profile/{now.year}/{now.month}/{now.day}/{instance}'
    ext = filename.split('.')[-1]
    uuid = uuid4().hex
    
    if instance:
        filename = '{}_{}.{}'.format(uuid, instance, ext)
    else:
        filename = '{}.{}'.format(uuid, ext)
    return os.path.join(upload_to, filename)


class UserManager(BaseUserManager):
    def create_user(self, email, username, point, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            point=point,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, point, password=None):
        user = self.create_user(
            email,
            password=password,
            username=username,
            point=point,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    point = models.PositiveIntegerField(default=0)

    # 팔로우
    followings = models.ManyToManyField('self', symmetrical=False, related_name="followers", blank=True, verbose_name="팔로워")
    
    # 프로필 사진
    profile_image = models.ImageField(null=True, upload_to=rename_imagefile_to_uuid, storage=None, verbose_name="프로필 사진")
    
    account_inactive = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["point", "username"]

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
