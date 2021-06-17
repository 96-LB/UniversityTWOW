import os, core.data as data
from base64 import b64encode
from flask import Flask, redirect, url_for, request
from flask_discord import DiscordOAuth2Session, Unauthorized, requires_authorization

app = Flask('')
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = b64encode(os.getenv('SECRET_KEY').encode('utf-8'))
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true" #suppresses reverse-proxy http errors - proxy should already force https

for key in ['CLIENT_ID', 'CLIENT_SECRET', 'REDIRECT_URI', 'BOT_TOKEN']:
    key = 'DISCORD_' + key
    app.config[key] = os.environ[key]

discord = DiscordOAuth2Session(app)


@app.route('/')
def index():
    log = 'logout' if discord.authorized else 'login'
    url = url_for(log)
    return f'<a href="{url}">{log}</a>'

@app.route("/login")
def login():
    return discord.create_session(['identify'], prompt=False)

@app.route("/logout")
def logout():
    discord.revoke()
    return redirect(url_for('index'))

@app.route("/callback")
def callback():
    discord.callback()
    return redirect(url_for("me"))

@app.errorhandler(Unauthorized)
def redirect_unauthorized(error):
    return redirect(url_for("login"))

@app.route("/me")
@requires_authorization
def me():
    user = discord.fetch_user()
    dev = data.get('dev') or {}
    return f"""
    <html>
        <head>
            <title>{user.name}</title>
        </head>
        <body>
            <div>
                {user.id}
            </div>
            <img src='{user.avatar_url}' />
            <form action='/text' method="POST">
                <input type="text" name="text" value="{dev.get("text", "")}" placeholder="try typing something here!">
                <input type="radio" name="opt" value="a" {"checked" if dev.get("opt") == "a" else ""}>
                <input type="radio" name="opt" value="b" {"checked" if dev.get("opt") == "b" else ""}>
                <input type="radio" name="opt" value="c" {"checked" if dev.get("opt") == "c" else ""}>
                <input type="submit">
            </form>
        </body>
    </html>"""

@app.route('/text', methods=['POST'])
@requires_authorization
def text():
    data.set('dev', request.form.to_dict())
    return "data successfully saved."

app.run('0.0.0.0')