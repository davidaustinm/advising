from django.urls import path

from . import views

urlpatterns = [
    path("mth-placement/", views.index, name="index"),
]
