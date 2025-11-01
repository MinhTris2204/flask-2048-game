"""
Content routes: Guide, Strategy pages for SEO
"""

from flask import render_template
from config import app


@app.route('/guide')
@app.route('/huong-dan-choi')
def guide():
    """Trang hướng dẫn chơi game 2048"""
    return render_template('guide.html')


@app.route('/strategy')
@app.route('/chien-thuat')
def strategy():
    """Trang chiến thuật chơi game 2048"""
    return render_template('strategy.html')
