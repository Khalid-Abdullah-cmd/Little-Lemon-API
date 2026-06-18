from rest_framework import generics, permissions
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializer import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer , UserSerializer
from .permissions import IsManagerOrReadOnly, IsManager
from django.contrib.auth.models import Group, User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404










# Menu-items and Menu-item endpoints 
class MenuItemListCreate(generics.ListCreateAPIView):
    
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    
    
    
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    
    
    

#Groups endpoints 

@api_view(['GET', 'POST']) 
@permission_classes([IsManager])
def Manager_details(request):
    
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    

    
    elif request.method == 'POST':
        
        user_name = request.data.get('username')
        
        if not user_name:
            return Response({"message": "Username field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, username=user_name)
        m_group = Group.objects.get(name="Manager")
        
        user.groups.add(m_group)
        return Response({"message": f"User '{user_name}' promoted to Manager successfully"}, status=status.HTTP_201_CREATED)
            
            
        
        
        
        
        



