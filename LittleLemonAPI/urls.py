from django.urls import path
from .views import (
MenuItemListCreate,
MenuItemDetailView,
Manager_details,
Manager_deletion,
Delivery_Crew_details,
Remove_From_Crew,
Cart_List,
Order_List)


urlpatterns = [
    
    #menu-items
    path('menu-items',MenuItemListCreate.as_view()),
    path('menu-items/<int:pk>',MenuItemDetailView.as_view()),
    
        
    #User Group Management
    path('groups/manager/users', Manager_details),
    path('groups/manager/users/<int:id>', Manager_deletion), 
    path('groups/delivery-crew/users', Delivery_Crew_details), 
    path('groups/delivery-crew/users/<int:id>', Remove_From_Crew), 
    
    
    #Cart
    path('cart/menu-items', Cart_List),
    
    #Order
    path('orders', Order_List),
    path('orders/<int:pk>'),
    
    

]
