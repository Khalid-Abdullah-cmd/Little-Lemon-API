from rest_framework import generics, permissions
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializer import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer , UserSerializer
from .permissions import IsManagerOrReadOnly, IsManager
from django.contrib.auth.models import Group, User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated










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

#Managers
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
            
            
        
        
@api_view(['DELETE'])
@permission_classes([IsManager])
def Manager_deletion(request, id):
    
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    group = Group.objects.get(name='Manager')
    
    group.user_set.remove(user)
    return Response(status=status.HTTP_200_OK)
    
    
    
    
#Delivery crew
@api_view(['GET', 'POST']) 
@permission_classes([IsManager])
def Delivery_Crew_details(request):
    
    if request.method == 'GET':
        crew = User.objects.get(groups__name='Delivery crew')
        serializer = UserSerializer(crew, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        username = request.data.get("username")
        
        
        if not username:
            return Response({"message": "Username field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, username=username)
        group = Group.objects.filter(name='Delivery crew')
        
        user.groups.add(group)
           
        return Response({"message": f"User '{username}' promoted to Delivery Crew successfully"}, status=status.HTTP_201_CREATED)
    
            
        

@api_view(['GET', 'POST']) 
@permission_classes([IsManager])   
def Remove_From_Crew(request, id):
    
    
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    group = Group.objects.get(name='Delivery crew')
    
    group.user_set.remove(user)
    return Response(status=status.HTTP_200_OK)



#Cart

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def Cart_List(request):
    
    if request.method == 'GET':
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        
        return Response (serializer.data, status=status.HTTP_200_OK)
    
        
        
    elif request.method == 'POST':

        print(f"The authenticated user is: {request.user.username}")
        pass 
       
       
        
    elif request.method == 'DELETE':
        
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart Emptied"})