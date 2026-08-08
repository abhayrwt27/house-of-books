from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)
    biography = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/', blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    def update_rating(self):
        reviews = self.review_set.all()
        self.review_count = reviews.count()
        self.average_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        self.save() 

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property 
    def total(self):
        return sum(item.subtotal for item in self.cartitem_set.all())

    def __str__(self):
        return f"{self.user.username}'s Cart"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def subtotal(self):
        return self.book.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
class Order(models.Model):
    STATUS_CHOICES = [("Pending", "Pending"),
                      ("Confirmed", "Confirmed"),
                      ("Delivered", "Delivered"),
     ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    payment_method = models.CharField(max_length=50, default="COD")
    payment_status = models.CharField(max_length=50, default="Pending")
    shipping_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    @property
    def total_items(self):
        return self.orderitem_set.count()

    def __str__(self):
        return f"Order {self.id}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.price * self.quantity
    
    def __str__(self):
        return self.book.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "book"], name="unique_user_book_review")]

    def __str__(self):
        return f"{self.user.username}-{self.book.title}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="unique_user_book_wishlist")
        ]

        def __str__(self):
            return f"{self.user.username} - {self.book.title}"