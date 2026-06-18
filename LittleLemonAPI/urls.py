from django.urls import path
from .views import MenuItemListCreate, MenuItemDetailView, Manager_details
urlpatterns = [
    
    #menu-items
    path('menu-items',MenuItemListCreate.as_view()),
    path('menu-items/<int:pk>',MenuItemDetailView.as_view()),
    
        
    #User Group Management
    path('groups/manager/users', Manager_details),
    path('manager/users/<int:pk>'),
    path('delivery-crew/users'),
    path('delivery-crew/users/<int:id>'),
    
    #Cart
    path('cart/menu-items'),
    
    #Order
    path('orders'),
    path('orders/<int:pk>'),
    
    

]
