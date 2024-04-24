"""For:
        Creating the database schema using SQLAlchemy allows the
        database to be easily modified and updated as the project
        grows and changes. It also allows the schema to be translated
        between different database types, such as SQLite and MySQL.
"""

from modules.globals import db, app
from modules.helpers import hash_pw, encrypt, decrypt, session
from sqlalchemy import String, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, registry

cloud_db = registry(metadata=db.metadatas[None])



@cloud_db.mapped_as_dataclass()
class Credentials:
    """ credentials table in the database that is
        designed to store login information for users
    """

    __tablename__ = "credentials"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(ForeignKey("role.role_name"), nullable=False)


@cloud_db.mapped_as_dataclass()
class Role:
    """ role table in the database that is
        designed to store user roles to identify
        which permissions the user is allowed
    """

    __tablename__ = "role"

    role_name: Mapped[str] = mapped_column(String(1), primary_key=True)


@cloud_db.mapped_as_dataclass()
class UserEntryCloud:
    """ patient_info table in the database that is
        designed to store patient information
    """

    __tablename__ = "User_Entries"

    user_id: Mapped[int] = mapped_column(ForeignKey("credentials.user_id"), nullable=False)
    entry_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False, unique=True, nullable=False)
    site_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    site_username: Mapped[str] = mapped_column(String(50), nullable=False)
    site_password: Mapped[str] = mapped_column(LargeBinary, nullable=False)


app.logger.info("administrative: (4) database tables configured")

# create a SQLite database if one does not already exist
with app.app_context():
    db.create_all()
    app.logger.info("administrative: (5) database tables created")
    if not db.session.execute(db.select(Role)).scalars().fetchall():
        app.logger.info("administrative: (5a) populating database with test data")
        db.session.add_all([
            Role(role_name="H"),  # can access all fields of UserEntries, but not passwords
            Role(role_name="R"),  # can access all fields of UserEntries
            Credentials(username="admin", password=hash_pw("test"), role="H"),
            Credentials(username="user", password=hash_pw("test"), role="R"),
        ])
    db.session.commit()