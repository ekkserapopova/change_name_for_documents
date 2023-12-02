import redis
from rest_framework.permissions import BasePermission
from .models import CustomUser
from rest_framework import permissions

from change_surname.settings import REDIS_HOST, REDIS_PORT

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

class IsManager(BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return False
        
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        return False

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return False
        
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        return user.is_superuser
# class IsManager(permissions.BasePermission):
#     def has_permission(self, request, view):
#         print(request.user)
#         return bool(request.user and (request.user.is_staff or request.user.is_superuser))

# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_superuser)