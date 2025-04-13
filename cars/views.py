from django.shortcuts import render, redirect, get_object_or_404
from .models import Car, Brand
from .forms import CarForm, CarImageForm
from django.contrib.auth.decorators import login_required

def car_list(request):
    try:
        cars = Car.objects.filter(status='approved')
        brands = Brand.objects.all()
    except Exception as e:
        print(f"Error: {e}")
        cars = []
        brands = []
    return render(request, 'cars/car_list.html', {'cars': cars, 'brands': brands})

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk, status='approved')
    return render(request, 'cars/car_detail.html', {'car': car})

@login_required
def post_car(request):
    if request.method == 'POST':
        car_form = CarForm(request.POST)
        image_form = CarImageForm(request.POST, request.FILES)
        if car_form.is_valid() and image_form.is_valid():
            car = car_form.save(commit=False)
            car.user = request.user
            car.save()
            image = image_form.save(commit=False)
            image.car = car
            image.save()
	    # Tạo thông báo cho user "root" nếu người đăng không phải root
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
    return render(request, 'cars/post_car.html', {'car_form': car_form, 'image_form': image_form})
