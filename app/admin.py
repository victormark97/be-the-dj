from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser,
    DjProfile,
    Location,
    Event,
    Song,
    SongRequest
)

IMAGE_TAG = '<img src="data:image/png;base64,{}" width="320" height="320"/>'


class SoftDeletionModelAdmin(admin.ModelAdmin):
    readonly_fields = ('is_active',)

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save()

    def delete_queryset(self, request, queryset):
        queryset.update(is_active=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    actions = ['soft_delete_selected']
    
    def soft_delete_selected(self, request, queryset):
        queryset.update(is_active=False)

    soft_delete_selected.short_description = "Soft delete selected objects"


class DjProfileForm(forms.ModelForm):
    upload = forms.ImageField(required=False)
    class Meta:
        model = DjProfile
        fields = ('name', 'user', 'upload')

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            raise forms.ValidationError('User is required')
        return user
    
    def clean_upload(self):
        image = self.cleaned_data.get('upload')
        instance = self.instance
        instance.encode_image(image)
        return instance.image
    
    def display_image(self):
        if self.instance.image:
            return format_html(IMAGE_TAG, self.image)
        return '(No image)'
    
    display_image.short_description = 'Image Preview'

    readonly_fields = ('display_image',)


class DjProfileInline(admin.StackedInline):
    model = DjProfile
    form = DjProfileForm
    fields = ('name', 'upload', 'display_image',)
    readonly_fields = ('display_image',)

    @admin.display(description='Image')
    def display_image(self, instance):
        if instance.id and instance.image:
            return format_html(IMAGE_TAG, instance.image)
        return "(No image)"
    
    display_image.short_description = 'Image Preview'


@admin.register(DjProfile)
class DjProfileAdmin(SoftDeletionModelAdmin):
    form = DjProfileForm

    def dj_email(self, obj):
        return obj.user.email
    
    @admin.display(description='Image')
    def display_image(self, obj):
        return format_html(IMAGE_TAG, obj.image)

    list_display = ('name', 'dj_email', 'image_name')
    search_fields = ('name', 'dj_email')
    autocomplete_fields = ('user',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # if obj is not None, the page is for updating
            return ['display_image']
        else:  # else, the page is for creating
            return []

    dj_email.short_description = 'Dj Email'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, SoftDeletionModelAdmin):
    inlines = (DjProfileInline, )

    ordering = ('email',)

    list_display = ('email', 'is_dj','is_staff', 'is_active')

    # Update the fields used in the user creation form in the admin site
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    # Update the fields used in the user change form in the admin site
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Permissions'), {'fields': ('is_staff', 'is_active')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'is_superuser',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


@admin.register(Location)
class LocationAdmin(SoftDeletionModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'created_at')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(SoftDeletionModelAdmin):
    def dj_email(self, obj):
        return obj.dj.email
    
    def dj_name(self, obj):
        return obj.dj.djprofile.name
    
    def location_name(self, obj):
        return obj.location.name
    
    dj_email.short_description = 'Dj Email'
    dj_name.short_description = 'Dj Name'
    location_name.short_description = 'Location Name'

    list_display = ('name', 'dj_email', 'dj_name', 'location_name', 'start', 'end', 'is_live')
    search_fields = ('name', 'dj_email', 'dj_name', 'location_name', 'start', 'end', 'is_live')
    autocomplete_fields = ('dj', 'location')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'dj', 'location',  'start', 'end')}
        ),
    )
    
    # Update the fields used in the user change form in the admin site
    fieldsets = (
        (None, {'fields': ('name', 'dj', 'location', 'start', 'end')}),
    )

@admin.register(Song)
class SongAdmin(SoftDeletionModelAdmin):
    list_display = ('artist', 'name', 'spotify_url', 'created_at')
    search_fields = ('artist', 'name', 'spotify_url')

@admin.register(SongRequest)
class SongRequestAdmin(SoftDeletionModelAdmin):
    def song_name(self, obj):
        return obj.song.name
    
    def user_email(self, obj):
        return obj.user.email
    
    def dj_email(self, obj):
        return obj.dj.email

    def dj_name(self, obj):
        return obj.dj.djprofile.name
    
    def event_name(self, obj):
        return obj.event.name

    list_display = ('song', 'user', 'dj', 'event', 'status', 'last_status_timestamp')
    search_fields = ('song_name', 'user_email', 'dj_email', 'dj_name', 'event_name')
