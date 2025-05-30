"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""

from os import getenv
from typing import List

from cas import CASClientV3
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from models.users.users_model import User
from models.clubs.clubs_model import Club
from utils.mail_utils import send_email
from utils.session_utils import create_session, SESSION_COOKIE_NAME, invalidate_session


def inform_users(subscribers: List, subject: str, content: str) -> None:
    recipients = [
        {"name": user.first_name + " " + user.last_name, "email": user.email}
        for user in subscribers
    ]

    send_email(recipients, subject, content)


def get_batch(roll):
    roll = str(roll)
    year = roll[:4]
    rem = roll[4:]
    batch = year
    if (rem[0] in ("7", "8")) or rem[:3] == "900":
        batch = "PhD" + batch
    elif (rem[:2] in ("10", "11")) or rem[:3] == "909":
        batch = "UG" + batch
    elif rem[:2] in ("20", "21"):
        batch = "PG" + batch
    elif rem[:2] == "12":
        batch = "LE" + batch
    return batch


async def user_login_cas(
    response: Response,
    ticket: str,
    user_agent: str,
    ip_address: str,
    cas_client: CASClientV3,
    db: Session,
):
    if ticket:
        user, attributes, _ = cas_client.verify_ticket(ticket)
        if user:
            try:
                roll = attributes["RollNo"]
            except KeyError:
                roll = attributes["uid"]
            email = attributes["E-Mail"]
            first_name = attributes["FirstName"]
            last_name = attributes["LastName"]
            uid = attributes["uid"]

            # look up user in database
            db_user = db.query(User).filter(User.uid == uid).first()

            # create if user doesn't exist
            if not db_user:
                db_user = User(
                    uid=uid,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    roll_number=roll,
                    batch=get_batch(roll),
                    profile_picture=0,
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)

            # create session token and set cookie
            encrypted_session_id = create_session(
                user_uid=uid, user_agent=user_agent, ip_address=ip_address, db=db
            )
            response = RedirectResponse(url=f"{getenv('FRONTEND_URL')}/profile")
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=encrypted_session_id,
                httponly=True,
                secure=True,
                samesite="lax",  # protection against CSRF
            )
    return response


# log user out by invalidating their session
async def user_logout(response: Response, encrypted_session_id: str, db: Session):
    invalidate_session(encrypted_session_id, db)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return {"message": "Logged out successfully"}


async def get_clubs_by_user(user_id: str, db: Session):
    user = db.query(User).filter(User.uid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.clubs


def is_member_of_club(user_id: str, club_id: str, db: Session) -> bool:
    club = db.query(Club).filter(Club.cid == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return any(member.uid == user_id for member in club.members)


def is_admin_of_club(user_id: str, club_id: str, db: Session) -> bool:
    """
    The club admin is defined as the user whose email matches the club's email address.
    """
    club = db.query(Club).filter(Club.cid == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    user = db.query(User).filter(User.uid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.email == club.email  # type: ignore
