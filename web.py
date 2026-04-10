import os
import requests
import secrets

from flask import Flask, redirect, request, session, url_for, render_template
from config import client, guild, file, use_login

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

web = Flask(__name__)
web.secret_key = secrets.token_hex(16)


# Homepage
@web.route("/")
@use_login()
def home(user):
    return render_template("home.html", user=user)


# Status page
@web.route("/status")
@use_login()
def status(user):
    return render_template("status.html", user=user)


# Apply page
@web.route("/apply")
@use_login()
def apply(user):
    return render_template("apply.html", user=user)


# Profile page (REQUIRES LOGIN)
@web.route("/profile")
@use_login(required=True)
def profile(user):
    return render_template("profile.html", user=user)


# Application page (REQUIRES LOGIN)
@web.route("/apply/<id>")
@use_login(required=True)
def apply_app(id, user):

    apps = file.load("data", "apps")

    if id not in apps or apps[id]["status"] == "private":
        return redirect(url_for("apply"))
    
    if user["id"] in apps[id]["submissions"] or apps[id]["status"] == "closed":
        return redirect(url_for("status_app", id=id))

    return render_template("apply_app.html", user=user, apps=apps, id=id)


# Status per application (REQUIRES LOGIN)
@web.route("/status/<id>")
@use_login(required=True)
def status_app(id, user):

    apps = file.load("data", "apps")

    if id not in apps or apps[id]["status"] == "private":
        return redirect(url_for("status"))
    
    if user["id"] not in apps[id]["submissions"]:
        return redirect(url_for("apply_app", id=id))
    
    return render_template("status_app.html", user=user, apps=apps, id=id)


# Submit application (POST, REQUIRES LOGIN)
@web.route("/submit/<id>", methods=["POST"])
@use_login(required=True)
def submit_app(id, user):
    apps = file.load("data", "apps")

    if id not in apps or apps[id]["status"] == "private":
        return redirect(url_for("apply"))
    
    if user["id"] in apps[id]["submissions"] or apps[id]["status"] == "closed":
        return redirect(url_for("status_app", id=id))

    apps[id]["submissions"][user["id"]] = {
        "name": user["global_name"],
        "username": user["username"],
        "status": "pending",
        "answers": {
            question_id: {
                "name": question["name"],
                "description": question["description"],
                "answer": request.form.get(question_id)
            }
            for question_id, question in apps[id]["questions"].items()
        }
    }

    file.save("data", "apps", apps)

    return redirect(url_for("status_app", id=id))


# Redirect user to Discord login
@web.route("/login")
def login():
    return redirect((
        f"https://discord.com/oauth2/authorize"
        f"?client_id={client.id}"
        f"&redirect_uri={client.redirect}"
        f"&response_type=code"
        f"&scope=identify%20guilds.members.read"
    ))


# Discord callback
@web.route("/callback")
def callback():
    token = requests.post(
        f"{client.api}/oauth2/token",
        data={
            "client_id": client.id,
            "client_secret": client.secret,
            "grant_type": "authorization_code",
            "code": request.args.get("code"),
            "redirect_uri": client.redirect,
            "scope": "identify"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()["access_token"]

    user = requests.get(
        f"{client.api}/users/@me",
        headers={"Authorization": f"Bearer {token}"}
    ).json()

    member = requests.get(
        f"{client.api}/users/@me/guilds/{guild.id}/member",
        headers={"Authorization": f"Bearer {token}"}
    ).json()

    if member.get("roles") is None:
        print("Failed to get roles:", member)
        user["roles"] = []
    else:
        user["roles"] = member.get("roles")

    session["user"] = user

    return redirect(session.get("page", url_for("home")))


# Logout
@web.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(session["page"])


from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(web)

if __name__ == "__main__":
    web.run(host="0.0.0.0", port=client.port)