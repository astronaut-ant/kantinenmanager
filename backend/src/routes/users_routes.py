from src.models.user import User
from src.services.users_service import UsersService
from flask import Blueprint, request, jsonify

users_routes = Blueprint("users_routes", __name__, url_prefix="/users")


@users_routes.post("")
def create_user():
    user = User(
        username=request.form["username"],
        password=request.form["password"],
        user_group=request.form["user_group"],
    )
    id = UsersService.create_user(user)
    return jsonify({"id": id})
