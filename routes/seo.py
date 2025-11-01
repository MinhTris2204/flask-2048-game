"""
SEO routes: sitemap.xml, robots.txt
"""

from flask import Response, render_template, request
from config import app
from datetime import datetime


@app.route('/robots.txt')
def robots_txt():
    """Generate robots.txt file for search engine crawlers"""
    robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {request.url_root}sitemap.xml
"""
    return Response(robots_content, mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap_xml():
    """Generate sitemap.xml for search engines"""
    # Các trang chính của website
    pages = [
        {'loc': '/', 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': '/game', 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': '/login', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': '/register', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': '/leaderboard', 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': '/game-history', 'priority': '0.7', 'changefreq': 'weekly'},
        {'loc': '/premium/manage', 'priority': '0.7', 'changefreq': 'monthly'},
    ]
    
    # Force HTTPS cho production
    base_url = request.url_root.replace('http://', 'https://').rstrip('/')
    
    # Tạo sitemap XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{base_url}{page["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{page["priority"]}</priority>\n'
        xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    return Response(xml_content, mimetype='application/xml')
