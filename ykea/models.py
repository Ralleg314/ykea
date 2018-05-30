from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Item(models.Model):
    CATEGORIES = (
        ("beds", "Beds & mattressess"),
        ("furn", "Furniture, wardrobes & shelves"),
        ("sofa", "Sofas & armchairs"),
        ("table", "Tables & chairs"),
        ("texti","Textiles"),
        ("deco","Decoration & mirrors"),
        ("light","Lighting"),
        ("cook","Cookware"),
        ("tablw","Tableware"),
        ("taps","Taps & sinks"),
        ("org", "Organisers & storage accesories"),
        ("toys","Toys"),
        ("leis","Leisure"),
        ("safe","safety"),
        ("diy", "Do-it-yourself"),
        ("floor","Flooring"),
        ("plant","Plants & gardering"),
        ("food","Food & beverages")
    )
    item_number = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_new = models.BooleanField()
    size = models.CharField(max_length=40)
    instructions = models.FileField(upload_to="instructions")
    featured_photo = models.FileField(upload_to="featured_photo")
    category = models.CharField(max_length=5, choices=CATEGORIES)
    
    
    def __str__(self):
        return  ('[**NEW**]' if self.is_new else '') + "[" + self.category + "] [" + self.item_number + "] " + self.name + " - " + self.description + " (" + self.size + ") : " + str(self.price) + " €"

class Client(models.Model):
    #id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    money = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return (self.user.username +" " + str(self.money))
    
class Comercial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return (self.user.username)

class ShoppingCart(models.Model):
    #id = models.CharField(max_length=8, unique=True)
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    
    items = models.ManyToManyField(Item, through='CartItem')

    def __unicode__(self):
        return str(self.id)
    
    def __str__(self):
        return (str(self.id))
    

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE) #solo queremos un item de cada en el shoppingcart, el numero lo determina quantity

