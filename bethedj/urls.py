"""
URL configuration for bethedj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from app.views import CreateEventView, CreateLocationView, HomeView, LoginView, LogoutView, CreateSongRequestView

create_patterns = [
    path('location/', CreateLocationView.as_view(), name='create_location'),
    path('event/', CreateEventView.as_view(), name='create_event'),
    path('song_request/', CreateSongRequestView.as_view(), name='create_song_request'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='home/', permanent=True)),
    path('home/', HomeView.as_view(), name='home'),
    path('accounts/social-auth/', include('social_django.urls', namespace='social')),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Create -> the path included here will be /create/<pattern>
    path('create/', include((create_patterns, 'app'), namespace='create')),
]
