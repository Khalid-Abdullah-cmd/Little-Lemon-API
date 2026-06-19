from rest_framework import generics, permissions
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializer import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer , UserSerializer
from .permissions import IsManagerOrReadOnly, IsManager, IsDeliveryCrew
from django.contrib.auth.models import Group, User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from datetime import date
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.decorators import throttle_classes







# Menu-items and Menu-item endpoints 

#changed the CBV for Pagination
class MenuItemPagination(PageNumberPagination):
    page_size = 2         
    page_size_query_param = 'perpage' 
    max_page_size = 100

class MenuItemListCreate(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    pagination_class = MenuItemPagination
    throttle_classes = [AnonRateThrottle, UserRateThrottle] 

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        
        category_name = self.request.query_params.get('category')
        if category_name:
            
            queryset = queryset.filter(category__title__iexact=category_name)
            
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        ordering = self.request.query_params.get('ordering')
        if ordering:
            
            
            ordering_fields = ordering.split(',')
            queryset = queryset.order_by(*ordering_fields)
            
        return queryset
    
    
    
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    
    

#   Groups endpoints 

#Managers
@api_view(['GET', 'POST']) 
@permission_classes([IsManager])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
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
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def Manager_deletion(request, id):
    
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    group = Group.objects.get(name='Manager')
    
    group.user_set.remove(user)
    return Response(status=status.HTTP_204_NO_CONTENT)    
    
    
    
#Delivery crew
@api_view(['GET', 'POST']) 
@permission_classes([IsManager])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def Delivery_Crew_details(request):
    
    if request.method == 'GET':
        crew = User.objects.filter(groups__name='Delivery crew')
        serializer = UserSerializer(crew, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        username = request.data.get("username")
        
        
        if not username:
            return Response({"message": "Username field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, username=username)
        group = Group.objects.get(name='Delivery crew')
        
        user.groups.add(group)
           
        return Response({"message": f"User '{username}' promoted to Delivery Crew successfully"}, status=status.HTTP_201_CREATED)
    
            
        

@api_view(['DELETE']) 
@permission_classes([IsManager])
@throttle_classes([AnonRateThrottle, UserRateThrottle])   
def Remove_From_Crew(request, id):
    
    
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    group = Group.objects.get(name='Delivery crew')
    
    group.user_set.remove(user)
    return Response(status=status.HTTP_204_NO_CONTENT)



#Cart

@api_view(['GET', 'POST', 'DELETE'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def Cart_List(request):
    
    if request.method == 'GET':
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        
        return Response (serializer.data, status=status.HTTP_200_OK)
    
        
        
    elif request.method == 'POST':

        menuitem_id = request.data.get('menuitem')
        quantity = request.data.get('quantity')

        if not menuitem_id or not quantity:
            return Response({"message": "Both 'menuitem' and 'quantity' are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        menuitem = get_object_or_404(MenuItem, id=menuitem_id)
        
        
        try:
            quantity = int(quantity)
            
            if quantity <= 0:
                return Response({"message": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValueError:
            return Response({"message": "Quantity must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        unit_price = menuitem.price
        total_price = unit_price * quantity

        cart_item = Cart.objects.filter(user=request.user, menuitem=menuitem).first()
        
        if cart_item:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * unit_price
            cart_item.save()
            return Response({"message": f"Updated {menuitem.title} quantity in cart."}, status=status.HTTP_200_OK)
        else:
            Cart.objects.create(
                user=request.user,
                menuitem=menuitem,
                quantity=quantity,
                unit_price=unit_price,
                price=total_price
            )
            return Response({"message": f"Added {menuitem.title} to cart."}, status=status.HTTP_201_CREATED)
        
       
       
        
    elif request.method == 'DELETE':
        
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart Emptied"})
    
    
   
   
   
# Orders     
@api_view(['GET', 'POST']) 
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle]) 
def Order_List(request):
    
    if request.method == 'GET':
        
        user = request.user
        
        #added pagination 
        if user.groups.filter(name='Manager').exists():
            orders_data = Order.objects.all()
            
        elif user.groups.filter(name='Delivery crew').exists():
            orders_data = Order.objects.filter(delivery_crew=user) 
            
        else:
            
            orders_data = Order.objects.filter(user=user) 

        
        status_param = request.query_params.get('status')
        
        if status_param is not None:
            
            is_delivered = True if status_param == '1' else False
            orders_data = orders_data.filter(status=is_delivered)

        
        ordering = request.query_params.get('ordering')
        
        
        if ordering:
            
            ordering_fields = ordering.split(',')
            orders_data = orders_data.order_by(*ordering_fields)


        paginator = PageNumberPagination()
        paginator.page_size = 2 
        
        result_page = paginator.paginate_queryset(orders_data, request)
        
        serializer = OrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
            
    
        
        
    elif request.method == 'POST':
        
        cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response({"message": "Your cart is empty. Please add items before placing an order."}, status=status.HTTP_400_BAD_REQUEST)
        


        total_price = sum([item.price for item in cart_items])
        
        order = Order.objects.create(
            user=request.user,
            status=False, # 0 for out for delivery / not delivered yet
            total=total_price,
            date=date.today()
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            
            
        # deleted menu items after added to orders    
        cart_items.delete()
        
        return Response({"message": f"Order #{order.id} for {order.user} on {order.date} placed successfully!"}, status=status.HTTP_201_CREATED)
    
   
   
   
   
        

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def Order_Detail(request, pk):
    
    
    order = get_object_or_404(Order, pk=pk)
    user = request.user
    
    # Determine the user's role
    is_manager = user.groups.filter(name='Manager').exists()
    is_delivery_crew = user.groups.filter(name='Delivery crew').exists()
    is_customer = not is_manager and not is_delivery_crew

    # get request
    if request.method == 'GET':
        
        if is_customer and order.user != user:
            return Response({"message": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)
        
        
        if is_delivery_crew and order.delivery_crew != user:
             return Response({"message": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)
            
        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #put request
    elif request.method in ['PUT', 'PATCH']:
        
        
        if is_customer:
            return Response({"message": "Customers cannot update orders."}, status=status.HTTP_403_FORBIDDEN)
        
        
        
        if is_delivery_crew:
            if 'status' in request.data:
                order.status = request.data.get('status')
                order.save()
                return Response({"message": "Order status updated by delivery crew."}, status=status.HTTP_200_OK)
            return Response({"message": "Delivery crew can only update the order status."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        if is_manager:


            if 'delivery_crew' in request.data:
                crew_id = request.data.get('delivery_crew')
                try:
                    crew_user = User.objects.get(pk=crew_id)
                    order.delivery_crew = crew_user
                except User.DoesNotExist:
                    return Response({"message": "Delivery crew user not found."}, status=status.HTTP_404_NOT_FOUND)
                    
            
            
            if 'status' in request.data:
                order.status = request.data.get('status')
            
            order.save()
            
            return Response({"message": "Order updated successfully by manager."}, status=status.HTTP_200_OK)

    #delete request
    elif request.method == 'DELETE':
        if is_manager:
            
            order.delete()
            return Response({"message": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        

        return Response({"message": "Only managers can delete orders."}, status=status.HTTP_403_FORBIDDEN)            
            
                
            
        
        
        
    