import core.data as data
from core.web import app, discord
from flask_discord import requires_authorization
from flask import request, render_template

@app.route('/')
def index():
    return render_template('index.html')

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