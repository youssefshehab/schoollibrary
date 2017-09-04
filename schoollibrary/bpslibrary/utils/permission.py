from functools import wraps
from flask import flash, redirect, request
from flask_login import current_user
from bpslibrary import login_manager
from bpslibrary.models import User
from bpslibrary.utils.nav import redirect_to_previous


def admin_access_required(func):
    """View decorator to restrict access to admin users.

    If you decorate a view with this, it will ensure that the current user
    is logged in and has admin rights before calling the actual view.

    Example::

        @app.route('/update')
        @admin_access_required
        def update():
            pass

    :param func: The view function to decorate.
    :type func: function
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        elif not current_user.is_admin:
            flash("You are not authorised to access this page.", 'error')
            return redirect_to_previous(True)

        return func(*args, **kwargs)

    return decorated_view
