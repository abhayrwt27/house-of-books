from django.contrib import admin
from .models import Genre, Author, Book, Cart, CartItem, Order, OrderItem, Review, Wishlist

admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Wishlist)