from django.urls import path

from . import views

urlpatterns = [
    path(
        "orders/<int:order_id>/recommend-box/",
        views.recommend_box_view,
        name="recommend-box",
    ),
]
