from rest_framework import permissions
from corsheaders.signals import check_request_enabled

def cors_allow_api_to_everyone(sender, request, **kwargs):
    return request.path.startswith('/api/')

check_request_enabled.connect(cors_allow_api_to_everyone)

class IsCommercialOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return request.user.groups.filter(name='Commercials').exists() 


##
##  LINK UTIL:
##
##  http://www.django-rest-framework.org/api-guide/permissions/
##
