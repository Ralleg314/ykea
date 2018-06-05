from django.shortcuts import render
from django.http import HttpResponse
from .models import Item, ShoppingCart, CartItem, Client, Bill, BillItem
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import ItemSerializer
from .permissions import IsCommercialOrReadOnly
from rest_framework.decorators import permission_classes

  

def index(request):
    items = Item.CATEGORIES
    context = {'items':items}
    
    if request.user.is_authenticated():
        context['money'] = Client.objects.get(user=request.user).money
    return render(request, 'ykea/index.html', context)



def items(request, category=""):
    items_by_category = Item.objects.filter(category=category)
    context = {
        'items': items_by_category,
        'category': category,
    }
    
    if request.user.is_authenticated():
        context['money'] = Client.objects.get(user=request.user).money
    return render(request, 'ykea/items.html', context)



def product(request, item_number=""):
    if item_number:
         product = Item.objects.get(item_number=item_number)
    
    
    context = {'product':product}
    
    if request.user.is_authenticated():
        context['money'] = Client.objects.get(user=request.user).money
    return render(request, 'ykea/product.html', context)



@login_required
def shoppingcart(request):
    if "cart" not in request.session:
      
        cart = ShoppingCart.objects.create(user=Client.objects.get(user=request.user))
        
        request.session["cart"] = cart.pk
    else:
        cart = ShoppingCart.objects.get(pk = request.session["cart"])
        
    if "selectedItem" in request.session:
    	  selectedItems = request.session["selectedItem"]
    else:
        selectedItems = []
    
    for key in request.POST:
        if key.startswith("checkbox"):
            if request.POST[key] not in selectedItems:
                selectedItems.append(request.POST[key])
            if Item.objects.get(item_number=request.POST[key]) not in cart.items.all():
                CartItem.objects.create(item=Item.objects.get(item_number=request.POST[key]), cart=cart, quantity=1)
                
    request.session["selectedItem"] = selectedItems
    request.session["cart"] = cart.id
    return HttpResponseRedirect(reverse('buy'))



def buy(request):
    if "cart" not in request.session:
        cart = ShoppingCart.objects.create()
        request.session["cart"] = cart.pk
    else:
        cart = ShoppingCart.objects.get(pk = request.session["cart"])
        
    context ={'cartItems' : CartItem.objects.filter(cart = request.session["cart"]), 'money' : Client.objects.get(user=request.user).money}
    return render(request, 'ykea/shoppingcart.html', context)



def process(request):
    if 'deleteButton' in request.POST:
        return cartDelete(request)
    if 'checkOutButton' in request.POST:
        return cartCheckOut(request)
    return HttpResponseRedirect(reverse('buy')) 


def cartDelete(request):
    if "cart" not in request.session:
        cart = ShoppingCart.objects.create()
        request.session["cart"] = cart.pk
    else:
        cart = ShoppingCart.objects.get(pk = request.session["cart"])
        
    if "selectedItem" in request.session:
    	  selectedItems = request.session["selectedItem"]
    else:
        selectedItems = []
    
    for key in request.POST:
        if key.startswith("checkbox"):
            if request.POST[key] in selectedItems:
                selectedItems.remove(request.POST[key]) #lo quitamos de selected items
                
            if Item.objects.get(item_number=request.POST[key]) in cart.items.all(): 
                #si esta lo borramos, si no... pues no lo borramos porque no podemos, pero si pudieramos lo hariamos
                for item in CartItem.objects.filter(cart = cart, item=Item.objects.get(item_number=request.POST[key])): #elimina todas las instancias de este objeto
                    item.delete()
                
    request.session["selectedItem"] = selectedItems
    request.session["cart"] = cart.id
    return HttpResponseRedirect(reverse('buy'))
                
    
    
def cartCheckOut(request):
    
    if "cart" not in request.session:
        cart = ShoppingCart.objects.create()
        request.session["cart"] = cart.pk
    else:
        cart = ShoppingCart.objects.get(pk = request.session["cart"])
        
    if "selectedItem" in request.session:
    	  selectedItems = request.session["selectedItem"]
    else:
        selectedItems = []
        
    for item,qty in zip(selectedItems, request.POST.getlist('qty')):
        itemcart = CartItem.objects.filter(cart = cart).get(item=Item.objects.get(item_number=item))
        itemcart.delete()
        
        if int(qty) == 0:
            selectedItems.remove(item)
        else:
            CartItem.objects.create(item=Item.objects.get(item_number=item), cart=cart, quantity=int(qty))
            
    
    totalprice = 0
    dinero = Client.objects.get(user=request.user).money
    for itemCart in CartItem.objects.filter(cart = request.session["cart"]):
        totalprice += (itemCart.quantity * itemCart.item.price)
      
    if totalprice>dinero:
        #############################################
        #MENSAJE DE ERROR NO TIENE SUFICIENTE DINERO#
        #############################################
        return HttpResponseRedirect(reverse('buy'))
    
    cliente = Client.objects.get(user=request.user)
    cliente.money = dinero-totalprice
    cliente.save()
    
    bill = Bill.objects.create(user=Client.objects.get(user=request.user),total = totalprice)
    itemsBought = []
    for itemCart in CartItem.objects.filter(cart = request.session["cart"]):
        billline = BillItem.objects.create(quantity = itemCart.quantity, cart = bill, item = itemCart.item)
        
        itemsBought.append((itemCart.item,itemCart.quantity))
        
    context ={'cartItems' : itemsBought, 'money' : Client.objects.get(user=request.user).money, 'totalprice' : totalprice}
    cart.delete()
    del request.session["cart"]
    del request.session["selectedItem"]
    return render(request, 'ykea/checkout.html', context)



def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/account/loggedin/")
    else:
        
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")
    
    
    
def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_client = Client.objects.create(user=new_user, money=100)
            
            #messages.info(request, "Thanks for registering. You are now logged in.")
            new_user = auth.authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            auth.login(request, new_user)
            
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })



def view_bills(request):
    context = {'bills' : Bill.objects.filter(user=Client.objects.get(user=request.user))}
    if request.user.is_authenticated():
        context['money'] = Client.objects.get(user=request.user).money
    return render(request, 'ykea/bills.html', context) 
       
   
def comparator(request, ips):
    items = Item.CATEGORIES
    context = {'items':items,'ips':ips}
    
    return render(request, 'ykea/comparator.html', context)


@permission_classes((IsCommercialOrReadOnly, ))
class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Items to be viewed or edited.
    """
    queryset = Item.objects.all().order_by('item_number')
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        queryset = Item.objects.all().order_by('item_number')
        
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category=category)
            
        new = self.request.query_params.get('new', None)
        if new is not None:
            queryset = queryset.filter(is_new=new)
            
        price = self.request.query_params.get('price', None)
        if price is not None:
            queryset = queryset.filter(price__lte=price)
        
		return queryset
