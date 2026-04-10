import os
import json

from functools import wraps

from flask import session, redirect, url_for, request

class client():

    id = "YOUR_CLIENT_ID"
    secret = "YOUR_CLIENT_SECRET"
    port = 5067
    redirect = "https://yourdomain.com/callback"

    api = "https://discord.com/api"

    token = "YOUR_BOT_TOKEN"

class guild():

    id = 0  # YOUR_GUILD_ID

class file():
    
    def load(folder, file):
        return json.load(open(os.path.join(folder, f"{file}.json"), "r"))
    
    def save(folder, file, data):
        return json.dump(data, open(os.path.join(folder, f"{file}.json"), "w"), indent=4)
    
def use_login(required=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == "GET":
                if request.endpoint not in ("login", "callback", "static"):
                    session["page"] = request.url

            else:
                session["page"] = request.referrer or url_for("home")

            user = session.get("user")

            if required and user is None:
                return redirect(url_for("login"))

            return func(*args, user=user, **kwargs)

        return wrapper
    return decorator
