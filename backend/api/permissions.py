from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission): 
    
    def has_permission(self, request, view): 
        return( 
            request.method in permissions.SAFE_METHODS 
            or request.user.is_authenticated 
        ) 

    def has_object_permission(self, request, view, obj): 
        if request.method in permissions.SAFE_METHODS: 
            return True 
        return obj.author == request.user

    

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_admin or user.is_superuser)