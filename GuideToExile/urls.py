"""GuideToExile URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.urls import path, include

from GuideToExile import views, settings

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('guide/new/', views.new_guide_view, name='new_guide'),
    path('guide/show/<int:pk>/<slug:slug>', views.show_guide_view, name='show_guide'),
    path('guide/edit/<int:pk>/', views.edit_guide_view, name='edit_guide'),
    path('guide/guide_tab/<int:pk>/', views.guide_tab_view, name='guide_tab'),
    path('guide/gear_gems_tab/<int:pk>/', views.gear_gems_tab_view, name='gear_gems_tab'),
    path('guide/skill_tree_tab<int:pk>/', views.skill_tree_tab_view, name='skill_tree_tab'),
    path('guide/addcomment/<int:guide_id>/', views.add_comment, name='add_comment'),
    path('guide/showcomments/<int:guide_id>/', views.show_comments, name='show_comments'),
    path('guide/deletecomment/', views.delete_comment, name='delete_comment'),
    path('guide/editcomment/', views.edit_comment, name='edit_comment'),
    path('profile/<slug:user_id>/<slug:username>', views.UserProfileView.as_view(), name='user_profile'),
    path('user/settings', views.user_settings_view, name='user_settings'),
    path('signup/', views.signup_view, name="signup"),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

# Add Django site authentication urls (for login, logout, password management)

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
