import requests

from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps


def login_required(f):
    """Decorator to ensure user is logged in"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function