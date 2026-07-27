from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path("add-to-cart/<int:book_id>/", views.add_to_cart, name='add_to_cart'),
    path("cart/", views.cart_view, name='cart'),
    path("remove/<int:item_id>/", views.remove_from_cart, name='remove_from_cart'),
    path("increase/<int:item_id>/", views.increase_quantity, name="increase_quantity"),
    path("decrease/<int:item_id>/", views.decrease_quantity, name="decrease_quantity"),
    path("order-success/", views.order_success, name="order_success"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("book/<int:book_id>/review/", views.review_book, name="review_book",),
    path("book/<int:book_id>/wishlist/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", views.wishlist, name="wishlist"),
]