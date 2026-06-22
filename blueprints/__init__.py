from extensions import Flask

# Each module's routes live in its own blueprint and are wired up here.


def register_blueprints(app: Flask) -> None:
    from .user.user import userBp
    from .userProfile.userProfile import userProfileBp
    from .resource.resource import resourceBp
    from .booking.booking import bookingBp
    from .notification.notification import notificationBp

    blueprints = [
        userBp,
        userProfileBp,
        resourceBp,
        bookingBp,
        notificationBp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)
