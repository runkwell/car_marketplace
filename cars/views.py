from django.shortcuts import render, redirect, get_object_or_404
from .models import Car, Brand, CarImage, Notification, PurchaseRequest
from .forms import CarForm, CarImageForm
from django.contrib import messages
from django.contrib.auth.models import User  
from django.contrib.auth.decorators import login_required  
from django.db.models import Q

def car_list(request):
    cars = Car.objects.filter(status='approved')
    brands = Brand.objects.all()

    # Lấy các tham số tìm kiếm từ request.GET
    query = request.GET.get('q', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    brand_id = request.GET.get('brand', '')
    condition = request.GET.get('condition', '')
    location = request.GET.get('location', '')

    # Lọc theo các tiêu chí
    if query:
        cars = cars.filter(
            Q(model__icontains=query) | Q(brand__name__icontains=query)
        )
    if price_min:
        try:
            price_min = float(price_min)
            cars = cars.filter(price__gte=price_min)
        except ValueError:
            pass
    if price_max:
        try:
            price_max = float(price_max)
            cars = cars.filter(price__lte=price_max)
        except ValueError:
            pass
    if brand_id:
        try:
            brand_id = int(brand_id)  # Đảm bảo brand_id là số nguyên
            cars = cars.filter(brand_id=brand_id)
        except ValueError:
            pass
    if condition:
        cars = cars.filter(condition=condition)
    if location:
        cars = cars.filter(location__icontains=location)

    # Lấy số thông báo chưa đọc
    unread_notifications_count = 0
    if request.user.is_authenticated and request.user.username == 'root':
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Thêm return để render template
    return render(request, 'cars/car_list.html', {
        'cars': cars,
        'brands': brands,
        'price_min': price_min,
        'price_max': price_max,
        'selected_brand': brand_id,
        'condition': condition,
        'location': location,
        'query': query,
        'unread_notifications_count': unread_notifications_count,
    })

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)

    # Lấy số thông báo chưa đọc
    unread_notifications_count = 0
    if request.user.is_authenticated and request.user.username == 'root':
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'cars/car_detail.html', {
        'car': car,
        'unread_notifications_count': unread_notifications_count,
    })


@login_required
def post_car(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Lấy số thông báo chưa đọc
    unread_notifications_count = 0
    if request.user.is_authenticated and request.user.username == 'root':
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    if request.method == 'POST':
        car_form = CarForm(request.POST)
        image_form = CarImageForm(request.POST, request.FILES)
        if car_form.is_valid() and image_form.is_valid():
            car = car_form.save(commit=False)
            car.user = request.user
            car.status = 'pending'
            car.save()
            
            image = image_form.save(commit=False)
            image.car = car
            image.save()
            
            if request.user.username != 'root':
                root_user = User.objects.get(username='root')
                Notification.objects.create(
                    user=root_user,
                    message=f"New car posted by {request.user.username}: {car.brand} {car.model}. Please review.",
                    car=car
                )
            
            messages.success(request, 'Car posted successfully! Waiting for approval.')
            return redirect('car_list')
    else:
        car_form = CarForm()
        image_form = CarImageForm()
    
    return render(request, 'cars/post_car.html', {
        'car_form': car_form,
        'image_form': image_form,
        'unread_notifications_count': unread_notifications_count,
    })

def notifications(request):
    if request.user.username != 'root':
        return redirect('car_list')
    
    notifications = request.user.notification_set.all().order_by('-created_at')
    
    # Lấy số thông báo chưa đọc
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'cars/notifications.html', {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    })


def approve_car(request, car_id):
    if request.user.username != 'root':
        return redirect('car_list')
    
    car = Car.objects.get(id=car_id)
    car.status = 'approved'
    car.save()
    
    # Đánh dấu thông báo liên quan là đã đọc
    notification = Notification.objects.get(car=car, user=request.user)
    notification.is_read = True
    notification.save()
    
    messages.success(request, f"Car {car.brand} {car.model} has been approved.")
    return redirect('notifications')

def buy_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, status='approved')

    # Lấy số thông báo chưa đọc
    unread_notifications_count = 0
    if request.user.is_authenticated and request.user.username == 'root':
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    if request.method == 'POST':
        buyer_name = request.POST.get('buyer_name')
        buyer_email = request.POST.get('buyer_email')
        buyer_phone = request.POST.get('buyer_phone')
        
        purchase = PurchaseRequest.objects.create(
            car=car,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone
        )
        
        root_user = User.objects.get(username='root')
        Notification.objects.create(
            user=root_user,
            message=f"Purchase request for {car.brand} {car.model} by {buyer_name}.",
            car=car
        )
        
        messages.success(request, 'Purchase request submitted successfully!')
        return redirect('car_list')
    
    return render(request, 'cars/buy_car.html', {
        'car': car,
        'unread_notifications_count': unread_notifications_count,
    })


def mark_sold(request, car_id):
    if request.user.username != 'root':
        return redirect('car_list')
    
    car = Car.objects.get(id=car_id)
    car.status = 'sold'
    car.save()
    
    # Đánh dấu thông báo liên quan là đã đọc
    notification = Notification.objects.get(car=car, user=request.user)
    notification.is_read = True
    notification.save()
    
    messages.success(request, f"Car {car.brand} {car.model} has been marked as sold.")
    return redirect('notifications')
