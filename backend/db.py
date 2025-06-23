from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy

db = SQLAlchemy()

class EncryptedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy = db.Column(db.String, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    wrapped_keys = db.relationship('WrappedKey', backref='data', lazy=True)

class AttributeKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    private_key = db.Column(db.LargeBinary, nullable=False)
    public_key = db.Column(db.LargeBinary, nullable=False)

class WrappedKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attribute_key.id'), nullable=False)
    data_id = db.Column(db.Integer, db.ForeignKey('encrypted_data.id'), nullable=False)
    wrapped_key = db.Column(db.LargeBinary, nullable=False)

