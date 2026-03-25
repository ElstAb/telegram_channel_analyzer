from app.db.session import SessionLocal
from app.db.models import User, Channel, UserChannel


def show_access_list():

    db = SessionLocal()

    rows = (
        db.query(User.username, Channel.channel_name)
        .join(UserChannel, User.id == UserChannel.user_id)
        .join(Channel, Channel.id == UserChannel.channel_id)
        .order_by(User.username, Channel.channel_name)
        .all()
    )

    if not rows:
        print("No access entries found")
        return

    print("\nUser        Channel")
    print("-----------------------")

    for username, channel in rows:
        print(f"{username:10} {channel}")


def add_access_menu():

    db = SessionLocal()

    while True:

        print("\nEnter: @username channel_name")
        print("Type 'back' to return")

        value = input("> ").strip()

        if value == "back":
            return

        try:

            username, channel_name = value.split(maxsplit=1)

            username = username.lstrip("@")

            user = db.query(User).filter_by(username=username).first()
            channel = db.query(Channel).filter_by(channel_name=channel_name).first()

            if not user:
                print("User not found. Ask user to write to the bot first so it can register them.")
                continue

            if not channel:
                # Auto-create channel record if it doesn't exist yet
                channel = Channel(channel_name=channel_name)
                db.add(channel)
                db.commit()

            exists = (
                db.query(UserChannel)
                .filter_by(user_id=user.id, channel_id=channel.id)
                .first()
            )

            if exists:
                print("Access already exists")
                continue

            access = UserChannel(
                user_id=user.id,
                channel_id=channel.id
            )

            db.add(access)
            db.commit()

            print("Access added")

        except ValueError:
            print("Invalid format. Use: @username channel_name")


def remove_access_menu():

    db = SessionLocal()

    while True:

        print("\nEnter: @username channel_name")
        print("Type 'back' to return")

        value = input("> ").strip()

        if value == "back":
            return

        try:

            username, channel_name = value.split(maxsplit=1)

            username = username.lstrip("@")

            user = db.query(User).filter_by(username=username).first()
            channel = db.query(Channel).filter_by(channel_name=channel_name).first()

            if not user or not channel:
                print("User or channel not found")
                continue

            access = (
                db.query(UserChannel)
                .filter_by(user_id=user.id, channel_id=channel.id)
                .first()
            )

            if not access:
                print("Access not found")
                continue

            db.delete(access)
            db.commit()

            print("Access removed")

        except ValueError:
            print("Invalid format. Use: @username channel_name")