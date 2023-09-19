# from django.shortcuts import render
# from django.views import View

# class IndexView(View):
#     def get(self, request):
#         return render(request, "index.html")


from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from photo.serializers import UserSerializer, GroupSerializer, ImagesSerializer
from .models import Photo



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImageViewSet(viewsets.ModelViewSet):

    queryset = Photo.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):

        context = super().get_serializer_context()
        context['request'] = self.request
        return context


    def get_queryset(self):

        return Photo.objects.filter(user=self.request.user)
    