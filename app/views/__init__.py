


def register_blueprints(app):
    from app.views.home import home
    from app.views.payment import payment
    from app.views.admin import admin
    from app.views.vend import vend

    app.register_blueprint(home)
    app.register_blueprint(payment)
    app.register_blueprint(admin)
    app.register_blueprint(vend)

    return app