from django.urls import path
from django.contrib.auth import views as auth_views

from hangMansApp import views

urlpatterns = [
    path('', views.Start, name='starting'),
    path('update/word', views.updateWord, name='updated-word-game'),
    path('hint/', views.get_hint, name='hint'),
    path('score/<uuid:share_id>/', views.share_score, name='share-score'),
    path('generate/word', views.generateWord, name='generate-word'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('history/', views.score_history, name='history'),
    path('<uuid:uui>', views.playShare, name='play-game-share'),
]
