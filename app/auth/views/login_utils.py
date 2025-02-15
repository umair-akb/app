from typing import Optional

from flask import session, redirect, url_for, request
from flask_login import login_user

from app.config import MFA_USER_ID
from app.log import LOG
from app.models import Referral


def after_login(user, next_url):
    """
    Redirect to the correct page after login.
    If user enables MFA: redirect user to MFA page
    Otherwise redirect to dashboard page if no next_url
    """
    if user.fido_enabled():
        # Use the same session for FIDO so that we can easily
        # switch between these two 2FA option
        session[MFA_USER_ID] = user.id
        if next_url:
            return redirect(url_for("auth.fido", next=next_url))
        else:
            return redirect(url_for("auth.fido"))
    elif user.enable_otp:
        session[MFA_USER_ID] = user.id
        if next_url:
            return redirect(url_for("auth.mfa", next=next_url))
        else:
            return redirect(url_for("auth.mfa"))
    else:
        LOG.d("log user %s in", user)
        login_user(user)

        # User comes to login page from another page
        if next_url:
            LOG.d("redirect user to %s", next_url)
            return redirect(next_url)
        else:
            LOG.d("redirect user to dashboard")
            return redirect(url_for("dashboard.index"))


# name of the cookie that stores the referral code
_REFERRAL_COOKIE = "slref"


def get_referral() -> Optional[Referral]:
    """Get the eventual referral stored in cookie"""
    # whether user arrives via a referral
    referral = None
    if request.cookies:
        ref_code = request.cookies.get(_REFERRAL_COOKIE)
        referral = Referral.get_by(code=ref_code)

    return referral
