from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Category
        fields = '__all__'
    
    
class MenuItemSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = models.MenuItem
        fields = '__all__'
        
        

        
class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Cart
        fields = '__all__'
    
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Order
        fields = '__all__'
        

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = '__all__'        
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'email']                       