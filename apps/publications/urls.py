from django.urls import path
from .views import *

app_name = 'publications'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('publication/<slug:slug>/', PublicationDetailView.as_view(), name='detail'),
    path('publication/<slug:slug>/ler/pagina/<int:page_number>/', reader_view, name='reader'),
]
