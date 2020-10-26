# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from data import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('create-project/', views.create_project, name='create-project'),
    path('add-data/<int:project_id>/', views.add_data, name='add-data'),
    path('aspect-topics/<int:project_id>/', views.aspect_topics, name='aspect-topics'),
    path('entities/<int:project_id>/', views.entities, name='entities'),
    path('top-entities/<int:project_id>/', views.top_entities, name='top-entities'),
    path('projects/<int:project_id>/', views.projects, name='projects'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
