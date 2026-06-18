from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=250, db_index=True)
    
    def __str__(self):
        return self.title
    
    
class MenuItem(models.Model):
    
    title = models.CharField(max_length=250, db_index=True)    
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.title
    


class Cart(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitems = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return str(self.id)
    
    #  Prevents duplicate rows for the same user/item combo
    class Meta:
        unique_together = ('user', 'menuitems')
    
    
class Order(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    delivery_crew = models.ForeignKey(User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='delivery_crew',
    blank=True)
    
    status = models.BooleanField(default=False, db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __str__(self):
        return str(self.id)
    
    
class OrderItem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        unique_together= ('order', 'menuitem')
    
            
    
    
          
    