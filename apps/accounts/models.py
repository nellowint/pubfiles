from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from core.utils import MediaPath, validate_file_size

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The user needs a valid email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        max_length=255,
        verbose_name='E-mail',
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Nome',
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Sobrenome',
    )
    avatar = models.ImageField(
        upload_to=MediaPath('avatars'),
        blank=True,
        null=True,
        verbose_name='Avatar',
        validators=[validate_file_size],
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name='E-mail verificado',
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Equipe',
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de entrada',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email
