from django.urls import path

from . import views

urlpatterns = [
    path("mth-placement/", views.index, name="index"),
    path("gv-enrollment/", views.enrollment, name="enrollment"),
    path("gv-enrollment/<str:dept>/", views.dept, name="department")
]
