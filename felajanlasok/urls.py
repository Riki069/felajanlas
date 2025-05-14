from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_data, name='upload'),
    path('3civil/', views.task3_civil, name='task3_civil'),
    path('4legtobb/', views.task4_legtobb, name='task4_legtobb'),
    path('5marc4/', views.task5_marc4, name='task5_marc4'),
    path('6hanyszor/', views.task6_hanyszor, name='task6_hanyszor'),
    path('7celonkent/', views.task7_celonkent, name='task7_celonkent'),
    path('8marcius/', views.task8_marcius, name='task8_marcius'),
]
