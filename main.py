from flask import Flask, render_template, request, url_for
import uuid
from vercel_wsgi import handle_request  # Tarvitaan Verceliin

app = Flask(__name__)
ip_storage = {}

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/create', methods=['POST'])
def create():
    random_id = str(uuid.uuid4())[:8]  
    ip_storage[random_id] = None
    track_link = url_for('track_ip', random_id=random_id, _external=True)
    check_link = url_for('check_ip', random_id=random_id, _external=True)
    return render_template(
        "link_created.html",
        track_link=track_link,
        check_link=check_link
    )

@app.route('/r/<random_id>')
def track_ip(random_id):
    if random_id not in ip_storage:
        return "Tuntematon ID", 404
    forwarded_for = request.headers.get('X-Forwarded-For', None)
    ip = forwarded_for.split(',')[0] if forwarded_for else request.remote_addr
    ip_storage[random_id] = ip
    return f'IP tallennettu: {ip} (ID: {random_id})'

@app.route('/check/<random_id>')
def check_ip(random_id):
    if random_id not in ip_storage:
        return "Tuntematon ID", 404
    ip = ip_storage[random_id]
    if ip:
        return f'Linkkiä on klikattu. Tallennettu IP: {ip}'
    else:
        return 'Linkkiä ei ole vielä klikattu.'

@app.route('/iplist')
def iplist():
    return '<br>'.join(f'{k}: {v}' for k, v in ip_storage.items())

# Vercel tarvitsee tämän käsittelijän
def handler(environ, start_response):
    return handle_request(app, environ, start_response)

