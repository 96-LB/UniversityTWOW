from core.web import app
from flask import render_template

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html',error=error), 404