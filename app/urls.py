from django.urls import path
from . import views


urlpatterns = [
    path('',views.login,name='login'),
    path('addmovie/',views.addMovie,name='setting'),
    path('addscreening/',views.addscreening,name='setting'),
    path('home/',views.home,name='home'),
    path('movies/<int:id>',views.movie,name='movie'),
    path('hall/<str:name>/<int:num>',views.hall,name='hall'),
    path('clear/<int:hall>/<int:movie>/<str:channelname>',views.clearSeat,name='hall'),
    path('booked_seat',views.booked_page,name='booked'),
    path('khalticheckout/<int:id>', views.khalticheckout, name='khalti'),
    path('verifyKhalti/', views.verifyKhalti, name='verifykhalti'),
    # path('data',views.automatedata) # to add data automatically
]