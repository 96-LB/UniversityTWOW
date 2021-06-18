from core.web import app

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

@app.errorhandler(404)
def error_404(error):
    return f'<h1>404 not found loser</h1><br>{error}'