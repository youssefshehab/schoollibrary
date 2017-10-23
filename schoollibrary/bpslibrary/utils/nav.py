
"""
Naviagtion
==========
"""

from urllib.parse import urlparse, urljoin
from flask import redirect, request, url_for
from flask_login import current_user
from bpslibrary import login_manager


def is_safe_url(target_url):
    """Determines if the url is safe.

    To protect from CSRF attacks it checks if the `target_url`
    is within the the site, and returns true if it, otherwise
    false.

    :param target_url: (str)
    The url to check.

    """
    host_url = urlparse(request.host_url)
    check_url = urlparse(urljoin(request.host_url, target_url))
    return host_url.netloc == check_url.netloc and \
        check_url.scheme in ('http', 'https')


def redirect_to_previous(avoid_current=False):
    """Redirects to the previous url or home.

    It checks first if the If the pervious url is safe, if it is
    it then determines checks teh `avoid_current` param. If url
    yielded, it redirects to home.

    :param `avoid_current`: (bool)
    If set to True, it ensures that no previous previous url
    or `referrer` is not looping back to current.

    """
    redirect_url = ''
    next_url = request.args.get('next')

    if next_url and is_safe_url(next_url):
        redirect_url = next_url
    elif request.referrer and is_safe_url(request.referrer):
        redirect_url = request.referrer

    if avoid_current and request.url == redirect_url:
        redirect_url = ''

    if current_user.is_authenticated \
       and url_for(login_manager.login_view) in redirect_url:
        redirect_url = ''

    return redirect(redirect_url)
