import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()


# ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    data = request.json
    if data is None or 'title' not in data or 'recipe' not in data:
        abort(400)
    title = data['title']
    recipe = json.dumps(data['recipe'])
    if title is None or recipe is None:
        abort(400)
    drink = Drink(title=title, recipe=recipe)
    try:
        drink.insert()
    except HTTPException:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    if request.json is None or 'title' not in request.json:
        abort(400)
    drink.title = request.json['title']
    if 'recipe' in request.json:
        drink.recipe = json.dumps(request.json['recipe'])
    try:
        drink.insert()
    except HTTPException:
        abort(422)
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
    except HTTPException:
        abort(422)
    return jsonify({
        "success": True,
        "delete": drink_id
    })


# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "message": error.error,
        "error": error.status_code
    }), error.status_code
