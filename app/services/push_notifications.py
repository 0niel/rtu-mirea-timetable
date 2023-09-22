from firebase_admin.messaging import Message, Notification, send

from app.firebase_client import firebase_client


async def send_push_notification(topic: str, title: str, body: str):
    message = Message(
        notification=Notification(
            title=title,
            body=body,
        ),
        topic=topic,
    )

    return send(message, app=firebase_client)
