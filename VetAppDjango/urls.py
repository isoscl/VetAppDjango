"""VetAppDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from VetApp import views, ajax

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^animal/$', views.AnimalView.as_view()),
    url(r'^owner/$', views.OwnerView.as_view(), name='Owner'),
    #url(r'^owner/(?P<id>\d+)/$', views.OwnerView.as_view(), name='Owner'),
    url(r'^$', views.IndexView.as_view(), name='VetApp'),
    url(r'^item/$', views.ItemView.as_view(), name='Item'),
    url(r'^visit/$', views.VisitView.as_view(), name='Visit'),
    url(r'^vet/$', views.VetView.as_view(), name='Vet'),
    url(r'^api/items/', views.items_search, name='search_items'),
    url(r'^api/operations/', views.operations_search, name='search_operations'),
    url(r'ajax_url/$', ajax.ajax_view, name='ajax_view'),
]
