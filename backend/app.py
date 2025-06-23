from flask import Flask, request, render_template, redirect, url_for, send_file
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import os
import sys
from pathlib import Path

if __package__ is None:
    # Support running the app directly from the backend directory
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from db import db, EncryptedData, AttributeKey, WrappedKey
    from abe import AttributeAuthority, encrypt, decrypt
else:
    from .db import db, EncryptedData, AttributeKey, WrappedKey
    from .abe import AttributeAuthority, encrypt, decrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
sslify = SSLify(app)

authority = AttributeAuthority()

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    data = EncryptedData.query.all()
    attributes = AttributeKey.query.all()
    return render_template('index.html', data=data, attributes=attributes)

@app.route('/generate_attribute', methods=['POST'])
def generate_attribute():
    name = request.form['name']
    if AttributeKey.query.filter_by(name=name).first():
        return redirect(url_for('index'))
    name, priv, pub = authority.generate_attribute(name)
    attr = AttributeKey(name=name, private_key=priv, public_key=pub)
    db.session.add(attr)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    message = request.form['message'].encode('utf-8')
    attrs = request.form.getlist('attributes')
    attrs_objs = AttributeKey.query.filter(AttributeKey.name.in_(attrs)).all()
    pub_keys = [a.public_key for a in attrs_objs]
    ciphertext, wrapped_keys = encrypt(message, pub_keys)
    encrypted = EncryptedData(policy=','.join(attrs), data=ciphertext)
    db.session.add(encrypted)
    db.session.commit()
    for attr_obj, wrapped in zip(attrs_objs, wrapped_keys):
        wk = WrappedKey(attribute_id=attr_obj.id, data_id=encrypted.id, wrapped_key=wrapped)
        db.session.add(wk)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/decrypt/<int:data_id>', methods=['POST'])
def decrypt_route(data_id):
    data = EncryptedData.query.get_or_404(data_id)
    attr_id = int(request.form['attribute'])
    attr = AttributeKey.query.get_or_404(attr_id)
    wrapped = WrappedKey.query.filter_by(data_id=data_id, attribute_id=attr_id).first()
    if not wrapped:
        return 'No access with this attribute', 403
    plaintext = decrypt(data.data, wrapped.wrapped_key, attr.private_key)
    return send_file(BytesIO(plaintext), as_attachment=True, download_name='decrypted.txt')

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    cert = base_dir / 'certs' / 'server.crt'
    key = base_dir / 'certs' / 'server.key'
    app.run(ssl_context=(str(cert), str(key)))
