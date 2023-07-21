import base64
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def one_day_from_now():
    return timezone.now() + timezone.timedelta(days=1)


class SoftDeletionModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeletionModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = SoftDeletionModelManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()


class ImageModel(models.Model):
    image = models.TextField(null=True, blank=True)
    image_name = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def encode_image(self, image):
        # Read image data and encode it into base64
        self.image_name = image.name
        image_data = image.read()
        self.image = base64.b64encode(image_data).decode()
        
    def decode_image(self):
        if self.image:
            format, imgstr = self.image.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=self.image_name + '.' + ext)
            return data
        return None


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('Password field must be set')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin, SoftDeletionModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_dj(self):
        try:
            self.djprofile
            return True
        except DjProfile.DoesNotExist:
            return False
        
    def __str__(self):
        return self.email

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
        'auth.Group', 
        blank=True, 
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        verbose_name=('groups')
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True, 
        related_name="%(app_label)s_%(class)s_related", 
        related_query_name="%(app_label)s_%(class)ss",
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )

class DjProfile(SoftDeletionModel, ImageModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)


class Location(SoftDeletionModel):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Event(SoftDeletionModel, ImageModel):
    name = models.CharField(max_length=255)
    dj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=one_day_from_now)

    def save(self, *args, **kwargs):
        if self.dj.djprofile is None:
            raise ValidationError("User must be a dj to be able to be assigned to an event")
        super().save(*args, **kwargs)

    @property
    def is_live(self):
        return self.start <= timezone.now() <= self.end

class Song(SoftDeletionModel):
    spotify_url = models.URLField(max_length=200)
    artist = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=200)


class SongRequest(SoftDeletionModel):
    REQUESTED = 'REQUESTED'
    PENDING = 'PENDING'
    PLAYED = 'PLAYED'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'

    STATUS_CHOICES = [
        (REQUESTED, 'Requested'),
        (PENDING, 'Pending'),
        (PLAYED, 'Played'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
    ]
    

    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_song_requests')
    dj = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dj_song_requests')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=REQUESTED)
    last_status_timestamp = models.DateTimeField(auto_now=True)

    ALLOWED_TRANSITIONS = {
        REQUESTED: [REJECTED, PENDING],
        PENDING: [EXPIRED, PLAYED]
    }

    def change_state(self, state):
        allowed_states = self.ALLOWED_TRANSITIONS.get(self.status)
        if allowed_states is None or state not in allowed_states:
            raise ValidationError(f'Transition from state ({self.status}) to ({state}) is not allowed')
        self.status = self.REJECTED
        self.last_status_timestamp = timezone.now()
        self.save()
        

    def reject(self):
        self.change_state(self.REJECTED)

    def start_processing(self):
        self.change_state(self.PENDING)
    
    def expire(self):
        self.change_state(self.EXPIRED)

    def play(self):
        self.change_state(self.PLAYED)