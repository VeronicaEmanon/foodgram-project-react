from rest_framework import permissions


class IsAuthorOrSuOrReadOnly(permissions.BasePermission): 
    
    def has_permission(self, request, view): 
        return( 
            request.method in permissions.SAFE_METHODS 
            or request.user.is_authenticated or request.user.is_superuser
        ) 

    def has_object_permission(self, request, view, obj): 
        if request.method in permissions.SAFE_METHODS: 
            return True 
        return obj.author == request.user
