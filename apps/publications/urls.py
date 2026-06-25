from django.urls import path

from .views import *

app_name = 'publications'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('publication/<slug:slug>/', PublicationDetailView.as_view(), name='detail'),
    path('publication/<slug:slug>/read/page/<int:page_number>/', reader_view, name='reader'),
    path('publication/<slug:slug>/comment/', add_comment, name='add_comment'),
    path('comment/<int:pk>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete_comment'),
    path('publication/<slug:slug>/rate/', rate_publication, name='rate'),
]
