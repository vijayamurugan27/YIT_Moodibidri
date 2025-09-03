from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"MenuItem('{self.name}', {self.price})"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"Customer('{self.name}', '{self.email}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    menu_item = db.relationship('MenuItem', backref=db.backref('orders', lazy=True))
    status = db.Column(db.String(50), nullable=False, default='pending')

    def __repr__(self):
        return f"Order({self.customer.name}, {self.menu_item.name}, {self.status})"

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_email = request.form['customer_email']
        menu_item_id = request.form['menu_item_id']

        customer = Customer(name=customer_name, email=customer_email)
        db.session.add(customer)
        db.session.flush()

        menu_item = MenuItem.query.get(menu_item_id)
        order = Order(customer=customer, menu_item=menu_item)
        db.session.add(order)
        db.session.commit()

        return redirect(url_for('home'))

    menu_items = MenuItem.query.all()
    return render_template('order.html', menu_items=menu_items)

@app.route('/owner')
def owner():
    orders = Order.query.all()
    received_orders = [order for order in orders if order.status == 'received']
    pending_orders = [order for order in orders if order.status == 'pending']
    delivered_orders = [order for order in orders if order.status == 'delivered']

    return render_template('owner.html', received_orders=received_orders, pending_orders=pending_orders, delivered_orders=delivered_orders)

@app.route('/update_status/<int:order_id>/<string:status>')
def update_status(order_id, status):
    order = Order.query.get(order_id)
    order.status = status
    db.session.commit()

    return redirect(url_for('owner'))

@app.route('/menu_app', methods=['GET', 'POST'])
def menu_app():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])

        menu_item = MenuItem(name=name, price=price)
        db.session.add(menu_item)
        db.session.commit()

        return redirect(url_for('menu_app'))

    return render_template('menu_app.html')

if __name__ == '__main__':
    app.run(debug=True)