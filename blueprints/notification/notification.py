from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, current_user_id,
)
from models import Notification

notificationBp = Blueprint("notification", __name__, url_prefix="/api/notification")


@notificationBp.get("")
@login_required
def list_notifications():
    """Feed the header bell: notifications + unread count."""
    rows = (
        Notification.query.filter_by(userId=current_user_id())
        .order_by(Notification.created_at.desc())
        .all()
    )
    unread = sum(1 for n in rows if not n.isRead)
    return jsonify(unread=unread, notifications=[n.to_dict() for n in rows])


@notificationBp.post("/<int:notification_id>/read")
@login_required
def mark_read(notification_id):
    """Mark a single notification as read."""
    n = Notification.query.get(notification_id)
    if not n or n.userId != current_user_id():
        abort(404, description="Notification not found.")
    n.isRead = True
    db.session.commit()
    return jsonify(notification=n.to_dict())


@notificationBp.post("/read-all")
@login_required
def mark_all_read():
    """Mark every notification for the current user as read."""
    Notification.query.filter_by(userId=current_user_id(), isRead=False).update(
        {"isRead": True}
    )
    db.session.commit()
    return jsonify(status="ok")
