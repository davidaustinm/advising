from django.urls import path

from . import views

urlpatterns = [
    path("mth-placement/", views.index, name="index"),
    path("gv-enrollment/", views.enrollment, name="enrollment"),
    path("gv-enrollment/MTH/", views.enrollment, name="department")
]
