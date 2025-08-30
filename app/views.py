from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .models import Product,Cart,Customer,OrderPlaced,Wishlist
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .forms import ReviewForm
from .models import Review
from django.db. models import Avg
from django.core.paginator import Paginator
from django.conf import settings
import razorpay
from .models import Payment 
from django.core.mail import send_mail
from .forms import ProductForm
from django.contrib .auth import authenticate,login as auth_login,logout


class ProdectHomeView(View):
 def get(self,request):
  totalitem = 0
  topwears = Product.objects.filter(category='TW')
  bottomwears = Product.objects.filter(category='BW')
  mobiles = Product.objects.filter(category='M')
  watches = Product.objects.filter(category='W')
   
  if request.user.is_authenticated:
    totalitem= len(Cart.objects.filter(user=request.user))
  return render(request, 'app/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'totalitem':totalitem,'watches':watches})


class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)
            ).exists()

        context = {
            'product': product,
            'item_already_in_cart': item_already_in_cart,
        }

        if request.user.is_authenticated and not request.user.is_staff:
            # Only for normal users
            all_reviews = Review.objects.filter(product=product).order_by('-created_at')
            review_form = ReviewForm()

            paginator = Paginator(all_reviews, 3)
            page_number = request.GET.get("page")
            page_reviews = paginator.get_page(page_number)

            avg_rating = all_reviews.aggregate(Avg('rating'))['rating__avg']
            if avg_rating is not None:
                avg_rating = round(avg_rating, 1)

            context.update({
                'review_form': review_form,
                'page_reviews': page_reviews,
                'avg_rating': avg_rating,
            })

        return render(request, 'app/productdetail.html', context)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if not request.user.is_authenticated or request.user.is_staff:
            return redirect('product-detail', pk=pk)

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

        return redirect('product-detail', pk=pk)

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)

    # Size check – only if category is TW or BW
    size = None
    if product.category in ['TW', 'BW']:
        size = request.GET.get('size')
        if not size:
            # Size is mandatory for TW/BW
            messages.warning(request, "Please select a size.")
            return redirect(f'/product-detail/{product.id}/')

    # Check if already in cart
    item_already = Cart.objects.filter(user=user, product=product).exists()
    if not item_already:
        Cart(user=user, product=product, size=size).save()
    
    return redirect('showcart')



@login_required
def show_cart(request):
 if request.user.is_authenticated:
  user = request.user
  carts = Cart.objects.filter(user=user)

  if not carts:
    return render(request, 'app/emptycart.html')

  amount = sum(item.quantity * item.product.discounted_price for item in carts)
  totalamount = amount + 30.0
  return render(request, 'app/showcart.html', {
    'cart': carts,  # ✅ key name बदला
    'amount': amount,
    'totalamount': totalamount,
    'shipping_amount': 30.0  # optional, जर वापरत असशील template मध्ये
})
 
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        amount = 0.0
        for item in Cart.objects.filter(user=request.user):
            amount += item.quantity * item.product.discounted_price

        totalamount = amount + 30.0

        return JsonResponse({
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        })
    

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        if c.quantity > 1:
         c.quantity -= 1
         c.save()

        amount = 0.0
        for item in Cart.objects.filter(user=request.user):
            amount += item.quantity * item.product.discounted_price

        totalamount = amount + 30.0

        return JsonResponse({
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        })    


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()

        amount = 0.0
        for item in Cart.objects.filter(user=request.user):
            amount += item.quantity * item.product.discounted_price

        totalamount = amount + 30.0

        return JsonResponse({
            'amount': amount,
            'totalamount': totalamount
        })    
def buy_now(request, pk):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=pk)
        Cart.objects.create(user=request.user, product=product, quantity=1)
        return redirect('checkout')
    else:
        return redirect('login')


@method_decorator(login_required,name='dispatch')
class ProfileView(View):
 def get(self,request):
  form =CustomerProfileForm()
  return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})
 def post(sef,request):
  form = CustomerProfileForm(request.POST)
  if form.is_valid():
   usr = request.user
   name =form.cleaned_data['name']
   locality =form.cleaned_data['locality']
   city =form.cleaned_data['city']
   state =form.cleaned_data['state']
   zipcode =form.cleaned_data['zipcode']
   reg = Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
   reg.save()
   messages.success(request,'Congratulation Your Profile Is Saved')
  return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})


@login_required
def address(request):
 add = Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})



def orders(request):
    order_data = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'app/orders.html', {'orders': order_data})


def mobile(request, data=None):
    if data is None:
        mobiles = Product.objects.filter(category='M')
    elif data in ['Redmi', 'Samsung']:
        mobiles = Product.objects.filter(category='M', brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M', discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M', discounted_price__gt=10000)
    else:
        mobiles = Product.objects.filter(category='M')  # fallback
    
    return render(request, 'app/mobile.html', {'mobiles': mobiles})

def watch(request,data=None):
    # watches = Product.objects.filter(category='W')
    # return render(request, 'app/watches.html', {'watches': watches})
    if data is None:
        watches = Product.objects.filter(category='W')
    elif data in ['Boat', 'Titan']:
        watches = Product.objects.filter(category='W', brand=data)
    elif data == 'below':
        watches = Product.objects.filter(category='W', discounted_price__lt=1000)
    elif data == 'above':
        watches = Product.objects.filter(category='W', discounted_price__gt=3000)
    else:
        watches = Product.objects.filter(category='W')  # fallback
    
    return render(request, 'app/watches.html', {'watches': watches})


def topwear(request):
    topwears = Product.objects.filter(category='TW')
    return render(request, 'app/topwear.html', {'topwears': topwears})

def bottomwear(request):
    bottomwears = Product.objects.filter(category='BW')
    return render(request, 'app/bottomwear.html', {'bottomwears': bottomwears})

def login(request):
 return render(request, 'app/login.html')
 
class CustomerRegistration(View):
#  id-pass rohity,R@183496
 def get(self,request):
  form= CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html',{'form':form})
 
 def post(self,request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request,'Congratulation Registerd Successfully.!!')
   form.save()
  return render(request, 'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):

    user = request.user
    cart = Cart.objects.filter(user=user)
    address = Customer.objects.filter(user=user)

    total = sum(item.quantity * item.product.discounted_price for item in cart)
    totalamount = total + 30  # delivery charge
    razoramount = int(totalamount * 100)  # in paise

    # Razorpay Client setup
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    data = { "amount": razoramount, "currency": "INR", "receipt": f"order_rcptid_{user.id}" }
    payment_response = client.order.create(data=data)

    # Save payment info
    payment = Payment.objects.create(
        user=user,
        amount=totalamount,
        razorpay_order_id=payment_response['id'],
        razorpay_payment_status=payment_response['status']
    )

    return render(request, 'app/checkout.html', {
        'addresses': address,
        'items': cart,
        'amount': total,
        'totalamount': totalamount,
        'razoramount': razoramount,
        'order_id': payment_response['id'],
        'razorpay_key_id': settings.RAZORPAY_API_KEY
    })




@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    user = request.user
    customer = Customer.objects.get(id=cust_id)
    payment = Payment.objects.get(razorpay_order_id=order_id)

    # Update payment info
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()

    # Place order
    cart = Cart.objects.filter(user=user)
    for item in cart:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=item.product,
            quantity=item.quantity,
            payment=payment
        )
    cart.delete()

    #  Email notification
    subject = 'Payment Successful - Order Confirmation'
    message = f'Hi {user.first_name},\n\nYour payment was successful.\nOrder ID: {order_id}\nPayment ID: {payment_id}\n\nThank you for shopping with us!'
    from_email = 'rohitseti.edu.in@gmail.com'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    return redirect('orders')


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(OrderPlaced, id=order_id, user=request.user)
    
    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()

        #  Send email
        subject = 'Your Order Has Been Cancelled'
        message = f"""
Hello {order.user.first_name},

Your order for "{order.product.title}" placed on {order.ordered_date.strftime('%d %B %Y')} has been successfully cancelled.

Order Details:
- Product: {order.product.title}
- Quantity: {order.quantity}
- Price: ₹{order.product.discounted_price}
- Status: Cancelled

Thank you for shopping with us.
        """
        recipient_email = order.user.email

        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)

        messages.success(request, "Order cancelled successfully and confirmation email sent.")
    else:
        messages.error(request, "Order cannot be cancelled at this stage.")

    return redirect('orders')


def search_view(request):
    
    query = request.GET.get('q')
    products = []
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query)
        ).distinct()
    return render(request, 'app/searchresult.html', {'products': products, 'query': query})



def is_admin(user):
    return user.is_authenticated and user.is_staff

def admin_login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(request, username=uname, password=pwd)
        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect('dashbord')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('adminlogin')
    
    return render(request, 'app/adminlogin.html')

def admin_logout(request):
    logout(request)
    return redirect('adminlogin')

@login_required
@user_passes_test(is_admin)
def dashbord(request):
    products = Product.objects.all()
    return render(request, 'app/dashbord.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashbord')
    else:
        form = ProductForm()
    return render(request, 'app/add.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('dashbord')
    else:
        form = ProductForm(instance=product)
    return render(request, 'app/add.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('dashbord')

