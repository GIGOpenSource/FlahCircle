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
        print(request.user.is_authenticated)
        print(request.user.is_creator)
        return request.user.is_authenticated and request.user.is_creator()


class IsAdminRole(permissions.BasePermission):
    """
    自定义权限类，只允许管理员用户访问
    """
    message = "需要管理员权限"
    def has_permission(self, request, view):
        # 检查用户是否已认证
        if not request.user or not request.user.is_authenticated:
            return False
        # 使用 User 模型中的 is_admin_role 方法检查是否为管理员
        return request.user.is_admin_role()

class IsAdminOrCreator(permissions.BasePermission):
    """
    自定义权限类：允许用户操作自己的数据，或管理员操作所有数据
    """
    message = "仅允许操作自己的数据或需要管理员权限"

    def has_object_permission(self, request, view, obj):
        # 检查用户是否已认证
        if not request.user or not request.user.is_authenticated:
            return False

        # 检查是否为管理员
        is_admin = IsAdminRole().has_permission(request, view)
        if is_admin:
            return True

        # 检查是否为对象所有者（假设obj有user字段指向User模型）
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id') and hasattr(request.user, 'id'):
            # 如果是User对象本身，则直接比较ID
            print(hasattr(obj, 'id'))
            print(obj.id == request.user.id)
            print(obj.id)
            print(request.user.id)
            return obj.id == request.user.id
        return False

    def has_permission(self, request, view):
        # 对于列表视图，只允许管理员访问
        if not request.user or not request.user.is_authenticated:
            return False
        # 对于列表视图的访问控制
        if view.action in ['list']:
            return IsAdminRole().has_permission(request, view)
        # 对于创建等操作，允许认证用户
        if view.action in ['create']:
            return True
        return True