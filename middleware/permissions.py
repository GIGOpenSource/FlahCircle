# core/permissions.py
from rest_framework import permissions

class IsVIP(permissions.BasePermission):
    """仅VIP及以上等级可见"""
    message = "需要VIP权限"
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.member_level in ['vip', 'svip']

class IsSVIP(permissions.BasePermission):
    """仅SVIP可见"""
    message = "需要SVIP权限"
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.member_level == 'svip'

from rest_framework import permissions

class IsCreator(permissions.BasePermission):
    """仅允许创作者访问"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_creator()