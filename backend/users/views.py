from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status 
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from api.pagination import CustomPagination
from api.serializers import FollowListSerializer, CustomUserSerializer, FollowSerializer, FollowListSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class =  CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            data = {
                "user": user.id,
                "author": author.id
            }
            serializer = FollowListSerializer(
                data=data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == "DELETE":
            subscription = get_object_or_404(
                Follow,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    
    