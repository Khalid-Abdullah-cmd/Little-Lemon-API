from rest_framework import permissions


from rest_framework import permissions


#to check if the user is a manager or not
class IsManagerOrReadOnly(permissions.BasePermission):
    

    def has_permission(self, request, view):
       
        #Get Request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        
        #Other Methods    
        if not (request.user and request.user.is_authenticated):
            return False
            
        return request.user.groups.filter(name='Manager').exists()
    
    
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not (request.user and request.user.is_authenticated):
            return False
            
        
        return request.user.groups.filter(name='Manager').exists()    