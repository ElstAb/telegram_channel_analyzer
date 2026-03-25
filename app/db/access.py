from app.db.session import SessionLocal
from app.db.models import User, Channel, UserChannel


def user_has_channel_access(telegram_id, channel_name):

    db = SessionLocal()

    user = db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()

    if not user:
        return False

    channel = db.query(Channel).filter(
        Channel.channel_name == channel_name
    ).first()

    if not channel:
        return False

    access = db.query(UserChannel).filter(
        UserChannel.user_id == user.id,
        UserChannel.channel_id == channel.id
    ).first()

    return access is not None