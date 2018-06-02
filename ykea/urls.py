from django.conf.urls import url, include
from django.contrib.auth.views import login, logout
from rest_framework import routers
from . import views

listOfAddresses = ['localhost',"sd2018-ykea-a1.herokuapp.com"]

urlpatterns = [
    url(r'^shoppingcart/$', views.shoppingcart, name='shoppingcart'),
    url(r'^process/$', views.process, name='process'),
    url(r'^buy/$', views.buy, name='buy'),
    url(r'^items/(?P<category>.*)/(?P<name>.*)/$', views.product, name='product'),
    url(r'^item/(?P<item_number>.*)/$', views.product, name='itemproduct'),
    url(r'^items/(?P<category>.*)/$', views.items, name='items'),
    url(r'^$', views.index, name='index'),
    url(r'^history/$', views.view_bills, name='bills'),
    url(r'^accounts/login/*', login , name='login_view'),
    url(r'^accounts/logout/*', logout, name='logout_view'),
    url(r'^register/$', views.register, name='register'),
    url(r'^comparator$', views.comparator, {'ips': listOfAddresses}),
]
