from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify
from database_setup import Restaurant, MenuItem, getSession

PAGE_TOP = "<html><body>"
PAGE_BOTTOM = "</html></body>"

session = getSession()

app = Flask(__name__)


@app.route('/')
@app.route('/restaurants/')
def listRestaurants():
    restaurants = getAllRestaurants()
    return render_template('restaurants.html',
                           restaurants=restaurants)


@app.route('/restaurants/<int:rest_id>/')
@app.route('/restaurants/<int:rest_id>/menu/')
def listRestaurantMenuItems(rest_id):
    restaurant = getRestaurantById(rest_id)
    items = getAllMenuItemsByRestaurantId(restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:rest_id>/menu/JSON')
def restaurantMenuJSON(rest_id):
    items = getAllMenuItemsByRestaurantId(rest_id)
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:rest_id>/menu/<int:item_id>/JSON')
def restaurantMenuItemJSON(rest_id, item_id):
    item = getMenuItemById(item_id)
    return jsonify(MenuItems=[item.serialize])


@app.route('/restaurants/add/', methods=['GET', 'POST'])
def addRestaurant():
    if request.method == 'GET':
        return render_template('addRestaurant.html')
    else:
        restaurant = Restaurant()
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash("New Restaurant Created")
        return redirect(url_for('listRestaurants'))


@app.route('/restaurants/<int:rest_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(rest_id):
    restaurant = getRestaurantById(rest_id)
    if request.method == 'GET':
        return render_template('editRestaurant.html', restaurant=restaurant)
    else:
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash("Restaurant name updated")
        return redirect(url_for('listRestaurants'))


@app.route('/restaurants/<int:rest_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(rest_id):
    restaurant = getRestaurantById(rest_id)
    if request.method == 'GET':
        return render_template('deleteRestaurant.html', rest_name=restaurant.name, rest_id=rest_id)
    else:
        session.delete(restaurant)
        session.commit()
        flash("Restaurant deleted")
        return redirect(url_for('listRestaurants'))


@app.route('/restaurants/<int:rest_id>/menu/add/', methods=['GET', 'POST'])
def addMenuItem(rest_id):
    if request.method == 'GET':
        return render_template('newmenuitem.html', rest_id=rest_id)
    else:
        item = MenuItem()
        item.restaurant_id = rest_id
        item.name = request.form['name']
        item.price = request.form['price']
        item.description = request.form['description']
        session.add(item)
        session.commit()
        flash("New Item Created")
        return redirect(url_for('listRestaurantMenuItems', rest_id=rest_id))


@app.route('/restaurants/<int:rest_id>/menu/<int:item_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(rest_id, item_id):
    menuItem = getMenuItemById(item_id)
    if request.method == 'GET':
        return render_template('editmenuitem.html',
                               rest_id=rest_id,
                               item_id=item_id,
                               item_name=menuItem.name,
                               item_price=menuItem.price,
                               item_description=menuItem.description)
    else:
        menuItem.name = request.form['name'] if request.form['name'] else menuItem.name
        menuItem.price = request.form['price'] if request.form['price'] else menuItem.price
        menuItem.description = request.form['description'] if request.form['description'] else menuItem.description
        session.add(menuItem)
        session.commit()
        flash("New Item Edited")
        return redirect(url_for('listRestaurantMenuItems', rest_id=rest_id))


@app.route('/restaurants/<int:rest_id>/menu/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(rest_id, item_id):
    menuItem = getMenuItemById(item_id)
    if request.method == 'GET':
        return render_template('deletemenuitem.html', rest_id=rest_id, item_id=item_id, item_name=menuItem.name)
    else:
        session.delete(menuItem)
        session.commit()
        flash("New Item Deleted")
        return redirect(url_for('listRestaurantMenuItems', rest_id=rest_id))


@app.route('/hello')
def helloWorld():
    return "Hello World"


def getAllRestaurants():
    return session.query(Restaurant).all()


def getAllMenuItemsByRestaurantId(restId):
    return session.query(MenuItem)\
        .filter(MenuItem.restaurant_id == restId)\
        .all()


def getRestaurantById(restId):
    """get instance of restaurant by given id."""
    return session.query(Restaurant).filter(Restaurant.id == restId).one()


def getMenuItemById(itemId):
    """get instance of menu item by given id."""
    return session.query(MenuItem).filter(MenuItem.id == itemId).one()


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
