from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Cart, CartItem, Order, OrderItem, Review, Wishlist, Genre, Author
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator


def home(request):
    search = request.GET.get("search","").strip()
    recommendations = []
    if search:
        books = Book.objects.filter(
            Q(title__icontains=search) | 
            Q(author__name__icontains=search) |
            Q(genre__name__icontains=search)
            )
        searched_book = books.first()
        if searched_book:
            same_genre = Book.objects.filter(genre=searched_book.genre).exclude(id=searched_book.id)
            same_author = Book.objects.filter(author=searched_book.author).exclude(id=searched_book.id)
            top_rated = Book.objects.order_by("-average_rating").exclude(id=searched_book.id)
            recommendations = (same_genre | same_author | top_rated).distinct()[:4]
        else:
            #No book found
            recommendations = Book.objects.all()[:4]

    else:
        books = Book.objects.all()

        sort_by = request.GET.get("sort")
        if sort_by == "price_low":
            books = books.order_by("price")
        elif sort_by == "price_high":
            books = books.order_by("-price")
        elif sort_by == "rating":
            books = books.order_by("-average_rating")
        elif sort_by == "title":
            books = books.order_by("title")

        genre_id = request.GET.get("genre")
        if genre_id:
            books = books.filter(genre_id = genre_id)

    paginator = Paginator(books, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "books/home.html",
                  {
                      "page_obj": page_obj,
                      "recommendations": recommendations,
                      "genres": Genre.objects.all(),
                  })

@login_required
def book_detail(request,id):
    book = Book.objects.get(id=id)
    recommended_books = Book.objects.filter(genre=book.genre).exclude(id=book.id)[:4]
    reviews = Review.objects.filter(book=book).select_related("user")
    return render(request,'books/book_detail.html', {'book':book, 'recommended_books':recommended_books, "reviews":reviews,})
    

@login_required
def add_to_cart(request, book_id):
    book = Book.objects.get(id=book_id)
    cart, created=Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Book added to cart!")
    return redirect("book_detail", id=book.id)

@login_required
def cart_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    return render(request, "books/cart.html", {
        "cart":cart,
        "cart_items":cart_items,
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart")

@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart")

@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart")    

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    if not cart_items.exists():
        return redirect("cart")

    if request.method == "POST":

        address = request.POST.get("address")
        city = request.POST.get("city")
        pin_code = request.POST.get("pin_code")
        phone_number = request.POST.get("phone_number")
        payment_method = request.POST.get("payment_method")
        shipping_address = f"{address}, {city}, {pin_code}"

        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total,
            status="Pending",
            shipping_address=shipping_address,
            phone_number=phone_number,
            payment_method=payment_method,
            payment_status="Pending",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price,
        )

        cart_items.delete()
        return redirect("order_success")

    return render(
        request, "books/checkout.html", {"cart": cart, "cart_items": cart_items,},
    )

@login_required
def order_success(request):
    return render(request, "books/order_success.html")

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-order_date")
    return render(request, "books/order_history.html",{"orders": orders,})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    return render(request, "books/order_detail.html", {"order": order, "order_items": order_items,})

@login_required
def review_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.get_or_create(
                user=request.user, 
                book=book, 
                defaults={"rating": form.cleaned_data["rating"],
                          "comment": form.cleaned_data["comment"],},)
        
            if not created:
                review.rating = form.cleaned_data["rating"]
                review.comment = form.cleaned_data["comment"]
                review.save()

            book.update_rating()

            messages.success(request, "Review submitted successfully!")
            return redirect("book_detail", id=book.id)

    else:
            form = ReviewForm()

    return render(request,"books/review_form.html",{"form":form, "book":book},)

@login_required
def toggle_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, book=book)

    if created:
        messages.success(request, "Book added to wishlist!")
    else:
        wishlist_item.delete()
        messages.warning(request, "Book removed from wishlist!")

    return redirect("book_detail", id=book.id)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("book")

    return render(request, "books/wishlist.html",{"wishlist_items": wishlist_items,},)

def categories(request):
    genres = Genre.objects.all()

    context = {"genres" : genres}

    return render(request, "books/categories.html", context)

def genre_books(request, genre_id):
    genre = get_object_or_404(Genre, id = genre_id)
    books = Book.objects.filter(genre=genre)

    context = {
        "genre" : genre,
        "books" : books,
    }

    return render(request, "books/genre_books.html", context)

def authors(request):
    authors = Author.objects.all()

    context = {"authors" : authors}

    return render(request, "books/authors.html", context)

def about(request):
    return render(request, "books/about.html")