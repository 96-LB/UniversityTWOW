from core.web import app
from flask import render_template

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html', error=error), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('403.html', error=error), 403

@app.errorhandler(500)
def error_500(error):
    return render_template('500.html', error=error), 500