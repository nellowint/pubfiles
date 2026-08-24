from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    path('click/<int:ad_id>/', views.increment_click, name='increment_click'),
]
