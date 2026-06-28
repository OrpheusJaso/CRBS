from extensions import Flask

# Each module's routes live in its own blueprint and are wired up here.


def register_blueprints(app: Flask) -> None:
    from .views.views import viewsBp
    from .user.user import userBp
    from .userProfile.userProfile import userProfileBp
    from .resource.resource import resourceBp
    from .booking.booking import bookingBp
    from .notification.notification import notificationBp
    from .dashboard.dashboard import dashboardBp
    from .equipment.equipment import equipmentBp
    from .equipment_manage.equipment_manage import equipmentManageBp
    from .report.report import reportBp
    from .issue.issue import issueBp

    blueprints = [
        viewsBp,
        userBp,
        userProfileBp,
        resourceBp,
        bookingBp,
        notificationBp,
        dashboardBp,
        equipmentBp,
        equipmentManageBp,
        reportBp,
        issueBp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)
