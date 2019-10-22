from datetime import datetime, timedelta
from billing_software import db, login_manager
from flask_login import UserMixin

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price= db.Column(db.Integer, nullable=False)
    weight= db.Column(db.Integer, nullable=True)
    date_created = db.Column(db.DateTime, nullable=True, default=datetime.now)
    # images = db.relationship('Pimages', foreign_keys=[id], backref='external')
    def __repr__(self):
        return f"Product('ID: {self.id}', 'Name: {self.name}', 'Price: {self.price}', 'Weight: {self.weight}' )"

class Pdimensions(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    length = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    piid = db.Column(db.Integer, db.ForeignKey('pimages.id'), nullable=True)
    prod_dimensions = db.relationship('Product', backref='dimensions', lazy=True)
    prod_images =db.relationship('Pimages', backref='image', lazy=True)
    def __repr__(self):
        return f"Dimensions('{self.pid}', '{self.length}', '{self.width}', '{self.prod_dimensions}' )"

class Pimages(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    porig = db.Column(db.BLOB)
    pprocess = db.Column(db.BLOB)
    prod_images = db.relationship('Product', backref='images', lazy=True)
    def __repr__(self):
        return f"Images('{self.id}', '{self.pid}', '<img src=\"data:image/png;base64',{self.porig}\" '/>', '{self.pprocess}' )"

class BillProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=True)
    prod_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    pquantity = db.Column(db.Integer, nullable=True, default=1)
    bill_products = db.relationship('Product', backref='info', lazy=True)
    bill = db.relationship('Bill', backref='products', lazy=True)
    def __repr__(self):
        return f"BillProducts('{self.bill_id}', '{self.prod_id}', '{self.pquantity}', 'bill_products: {self.bill_products}' )"

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_amount =  db.Column(db.Integer, nullable=True, default=0)
    date_created = db.Column(db.DateTime, nullable=True, default=datetime.now)
    def __repr__(self):
        return f"Bill('{self.id}', '{self.bill_amount}')"
