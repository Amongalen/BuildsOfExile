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
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from GuideToExile import views, settings

urlpatterns = [
    path('', views.index_view, name='index'),
    path('guide/list/', views.guide_list_view, name='guide_list'),
    path('my-guides/', login_required(views.my_guides_view), name='my_guides'),
    path('my-guides/list/', login_required(views.MyGuidesListView.as_view()), name='my_guides_list'),
    path('authors/', views.authors_view, name='authors'),
    path('authors/list/', views.authors_list_view, name='authors_list'),
    path('guide/new/', login_required(views.new_guide_pob_view), name='new_guide'),
    path('guide/show/<int:pk>/<slug:slug>/', views.show_guide_view, name='show_guide'),
    path('guide/draft/<int:pk>/', login_required(views.show_draft_view), name='show_draft'),
    path('guide/clear-draft/<int:pk>/', login_required(views.clear_draft_view), name='clear_draft'),
    path('guide/edit/<int:pk>/', login_required(views.edit_guide_view), name='edit_guide'),
    path('guide/edit-pob/<int:pk>/', login_required(views.edit_pob_view), name='edit_pob'),
    path('guide/cancel-edit/<int:pk>/', login_required(views.cancel_edit_view), name='cancel_edit'),
    path('guide/publish/<int:pk>/', login_required(views.publish_guide_view), name='publish_guide'),
    path('guide/archive/<int:pk>/', login_required(views.archive_guide_view), name='archive_guide'),
    path('guide/unarchive/<int:pk>/', login_required(views.unarchive_guide_view), name='unarchive_guide'),
    path('guide/liked/', login_required(views.LikedGuidesView.as_view()), name='liked_guides'),
    path('guide/get-likes/<int:pk>/', views.guide_likes, name='guide_likes'),
    path('guide/add-like/<int:pk>/', login_required(views.add_guide_like), name='add_like'),
    path('guide/remove-like/<int:pk>/', login_required(views.remove_guide_like), name='remove_like'),
    path('guide/guide-tab/<int:pk>/', views.guide_tab_view, name='guide_tab'),
    path('guide/gear-gems-tab/<int:pk>/', views.gear_gems_tab_view, name='gear_gems_tab'),
    path('guide/skill-tree-tab/<int:pk>/', views.skill_tree_tab_view, name='skill_tree_tab'),
    path('guide/addcomment/<int:guide_id>/', login_required(views.add_comment), name='add_comment'),
    path('guide/showcomments/<int:guide_id>/', views.show_comments, name='show_comments'),
    path('guide/deletecomment/', login_required(views.delete_comment), name='delete_comment'),
    path('guide/editcomment/', login_required(views.edit_comment), name='edit_comment'),
    path('user/settings/', login_required(views.user_settings_view), name='user_settings'),
    path('user/delete/', login_required(views.delete_user_view), name='delete_user'),
    path('signup/', views.signup_view, name="signup"),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('cookies-policy', views.CookiePolicy.as_view(), name='cookie_policy'),
    path('privacy-policy', views.PrivacyPolicy.as_view(), name='privacy_policy'),
    path('terms-of-use', views.TermsOfUse.as_view(), name='terms_of_use'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

# Add Django site authentication urls (for login, logout, password management)

urlpatterns += [
    path('accounts/', include('allauth.urls')),
]

urlpatterns += [
    path('admin/', admin.site.urls),
]
