from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def trainer_required(view_func):
    """Allow only logged-in users with is_trainer=True."""

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_trainer:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper