from django.shortcuts import render,redirect
from django.http import HttpResponse
from datetime import datetime 
from .models import *
from django.contrib.auth import authenticate,login as auth_login
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
from django.shortcuts import get_object_or_404
import json
from .forms import CreateMovie,CreateScreening


def hall(request, name, num):
    movie = get_object_or_404(Movie, movie_name=name)
    screening = Screening.objects.get(movie=movie)

    # Fetch bookings for the screening
    booked_seat_details = BookingDetail.objects.filter(booking__screening=screening)
    booked_seats = booked_seat_details.values_list('seat__seat_number', flat=True)

    seatselected = SeatSelect.objects.filter(screening=screening).values_list('seat__seat_number', flat=True)


    now = datetime.now()
    seatclass = Seat_Class.objects.get(id=num)
    seats = Seat.objects.filter(seat_class=seatclass).all()

    formatted_now = now.strftime("%Y-%m-%d")
    context = {
        'current_time': formatted_now,
        'seats': seats,
        'name': name,
        'hall': num,
        'booked_seat': booked_seats,
        'movie': movie,
        'selectedseat': seatselected,
        'screening': screening
    }
    return render(request, 'hall.html', context)

def home(request):
    movie = Screening.objects.all()
    context= {'movies':movie}
    return render(request,'home.html',context)

def movie(request,id):
    print(id)
    movie = Movie.objects.get(id=id)
    screen = Screening.objects.get(movie=movie)
    return render(request,'movie.html',{'movie':screen})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            auth_login(request,user)
            return redirect('home')
        else:
            return  HttpResponse("Username or password is incorrect!!")
    return render(request,'login.html')
        


# # automated data to load in database to add new class make a newseat class and put it's id 
# def automatedata(request):
#     a= ['A','B','C','D','E','F']
#     b = range(1,14)
#     seats = [f'{row}{col}' for row in a for col in b ]
#     seatclass = Seat_Class.objects.get(id=1)
#     for seat in seats:
#         data = Seat.objects.create(seat_class=seatclass,seat_number=seat)
#         data.save()
#     return render(request,'app.html',context={'msg':'done'})



def clearSeat(req,hall,movie,channelname):
    movie = Movie.objects.get(id=movie)
    screening= Screening.objects.get(movie=movie,hall_no=hall)
    print(screening)
    seat_selected = SeatSelect.objects.filter(user=req.user, screening=screening,locked=False)
    print(seat_selected)
    seat_numbers = list(seat_selected.values_list('seat__seat_number', flat=True))
    message = {
            'type': 'seat_clear',
            'seats': seat_numbers,
            'status': 'deselected',
            }
    print(seat_selected)
    seat_selected.delete()
    channel_layer = get_channel_layer()
    print(channelname)
    async_to_sync(channel_layer.group_send)(  # conveting into sync
        channelname,
        {
            'type':'seat_clear',
            'message':json.dumps(message)
        }
    )
    return HttpResponse('removed')

# for broadcasting bought ticket
def bookedSeat(req,hall,movie,channelname):
    movie = Movie.objects.get(id=movie)
    screening= Screening.objects.get(movie=movie,hall_no=hall)
    seat_selected = SeatBooking.objects.filter(user=req.user,screening=screening)
    print(seat_selected)
    seat_numbers = list(seat_selected.values_list('seat__seat_number', flat=True))
    message = {
            'type': 'seat_updated',
            'seats': seat_numbers,
            'status': 'booked',
            }
    channel_layer = get_channel_layer()
    print(channelname)
    async_to_sync(channel_layer.group_send)(  # conveting into sync
        channelname,
        {
            'type':'seat_updated',
            'message':json.dumps(message)
        }
    )
    return HttpResponse('done')


from django.conf import settings

def add_username_to_context(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = 'Guest'
    return {
        'username': username
    }


def booked_page(request):
    seat = SeatBooking.objects.filter(user=request.user)
    print(seat)
    for booking in seat:
        print(booking)
        print(booking.details)
        for detail in booking.details.all():
            print(detail.seat.seat_number)

    return render(request,'booked.html',{'bookedseat':seat})


# Khalti integration

def khalticheckout(request,id):
    # URL oF KHALTi
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    if request.method == "GET" and request.user.is_authenticated:
        print('#######################')
        screening = Screening.objects.get(id=id)
        selected_seats = SeatSelect.objects.filter(user=request.user, screening=screening, locked=False)
        print(selected_seats)

        if not selected_seats.exists():
            return HttpResponse("No items selected", status=400)

        # Lock the seats
        selected_seats.update(locked=True)

        # Now, calculate the total price using the evaluated list
        selected_seats_updated = SeatSelect.objects.filter(user=request.user, screening=screening, locked=True)
        total_price = sum([seat.seat.seat_class.price for seat in selected_seats_updated])

        print(total_price)
        
        # Create a new booking
        booking = SeatBooking.objects.create(
            user=request.user,
            screening=screening,
            total_price=total_price,
            is_paid=False,
            status='Pending'
        )

        print(selected_seats_updated)
        # Link selected seats to the booking
        try:
            for seat_select in selected_seats_updated:
                price = seat_select.seat.seat_class.price
                booking_detail = BookingDetail.objects.create(
                    booking=booking,
                    seat=seat_select.seat,
                    price=price
                )
                print(f"BookingDetail created: {booking_detail}")
        except Exception as e:
            print(f"Error creating BookingDetail: {e}")
        

        
        # Transfer CartItems to OrderItems and calculate total price

        # Assuming you have defined return_url and purchase_order_id correctly
        return_url = "http://127.0.0.1:8000/verifyKhalti"  # Example return URL
        purchase_order_id = str(booking.purchase_order_id)  # Convert UUID to string

        # Prepare payload for the request
        payload = json.dumps({
            "return_url": return_url,
            "website_url": return_url,
            "amount": total_price*100,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Order #" + str(booking.id),
            "customer_info": {
                "name": 'lall',
                "email": "test@khalti.com",  # Use actual user email
                "phone": "9800000001"  # Use actual user phone
            }
        })
        headers = {
            'Authorization': 'Key live_secret_key_68791341fdd94846a146f0457ff7b455',
            'Content-Type': 'application/json'
        }

        print(payload)
        # Make the POST request to Khalti
        response = requests.post(url, headers=headers, data=payload)
        new_res = response.json()
        print(new_res)
        print(new_res.get('payment_url'))
    
        # Redirect to Khalti payment page
        return redirect(new_res.get('payment_url'))

    # Handle GET request or unauthenticated users
    return HttpResponse("Invalid request", status=400)


def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == 'GET':
        id = request.GET.get('purchase_order_id')
        status = request.GET.get('status')

        if status == 'Completed':

            headers = {
                'Authorization': 'key live_secret_key_68791341fdd94846a146f0457ff7b455',
                'Content-Type': 'application/json',
            }
            pidx = request.GET.get('pidx')
            print('pidx',pidx)
            data = json.dumps({
                'pidx':pidx
            })
            res = requests.request('POST',url,headers=headers,data=data)
            print('res',res)
            print('res text',res.text)
            new_res = res.json()
            print('new_res',new_res['total_amount'])

            orderinstance = SeatBooking.objects.filter(user=request.user, is_paid=False,purchase_order_id=id).first()
            orderinstance.transaction_id=new_res['transaction_id']
            orderinstance.status = new_res['status']
            orderinstance.paymentid = new_res['pidx']

            hall = orderinstance.screening.hall_no
            channelname = orderinstance.screening.movie.movie_name
            movie = orderinstance.screening.movie.pk

            bookedSeat(request,hall,movie,channelname)

            if new_res['status']=='Completed':
                orderinstance.is_paid=True
                orderinstance.save()
        if status == 'User canceled':
            orderinstance = SeatBooking.objects.filter(user=request.user, is_paid=False,purchase_order_id=id).first()
            
            hall = orderinstance.screening.hall_no
            channelname = orderinstance.screening.movie.movie_name
            movie = orderinstance.screening.movie.pk
            SeatSelect.objects.filter(user=request.user, screening=hall,locked=True).update(locked=False)
            clearSeat(request,hall,movie,channelname)
            orderinstance.delete()
            
        return redirect('home')
    



def addMovie(request):
    # if request.user.is_superuser:
        insert=CreateMovie()
        if request.method=='POST':
            insert = CreateMovie(request.POST,request.FILES)
            if insert.is_valid():
                insert.save()
                return redirect('upload')
            else:
                return HttpResponse("pls fill value correctly")

        return render(request,'setting.html',{'movie':insert})
    # else:
    #     return render(request,'setting.html')

def addscreening(request):
    # if request.user.is_superuser:
        insert=CreateScreening()
        if request.method=='POST':
            insert = CreateScreening(request.POST,request.FILES)
            if insert.is_valid():
                insert.save()
                return redirect('upload')
            else:
                return HttpResponse("pls fill value correctly")

        return render(request,'setting.html',{'screening':insert})
    # else:
    #     return render(request,'setting.html')