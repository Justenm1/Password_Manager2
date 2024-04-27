"""For:
        Creating the database schema using SQLAlchemy allows the
        database to be easily modified and updated as the project
        grows and changes. It also allows the schema to be translated
        between different database types, such as SQLite and MySQL.
"""

from modules.globals import db, app
from modules.helpers import hash_pw, decrypt, encrypt, increment_entry_count
from sqlalchemy import String, ForeignKey, LargeBinary, Integer
from sqlalchemy.orm import Mapped, mapped_column, registry
from typing import Optional

cloud_db = registry(metadata=db.metadatas[None])


@cloud_db.mapped_as_dataclass()
class Credentials:
    """ credentials table in the database that is
        designed to store login information for users
    """

    __tablename__ = "credentials"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    role: Mapped[str] = mapped_column(ForeignKey("role.role_name"), nullable=False)







@cloud_db.mapped_as_dataclass()
class Role:
    """ role table in the database that is
        designed to store user roles to identify
        which permissions the user is allowed
    """

    __tablename__ = "role"

    role_name: Mapped[str] = mapped_column(String(1), primary_key=True)


def entry_factory():
    class EntryBase:
        """ patient_info table in the database that is
            designed to store patient information
        """

        __tablename__ = "User_Entries"

        entry_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
        site_name: Mapped[str] = mapped_column(String(50), nullable=False)
        site_username: Mapped[str] = mapped_column(String(50), nullable=False)
        site_password: Mapped[str] = mapped_column(LargeBinary, nullable=False)
        user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('credentials.user_id'), nullable=True)

        def decrypt(self):
            "Decrypts the encrypted fields of the object"
            self.site_password = decrypt(self.site_password, self.entry_id)

        def __init__(self, site_name, site_username, site_password, user_id=None):
            """ Base class ctor to create an entry in the database.
                The passwords are encrypted before being stored in
                the database to protect its confidentiality.
                If user_id is provided, it associates the entry with that user."""
            self.entry_id = app.config['entries']
            self.site_name = site_name
            self.site_username = site_username
            self.site_password = encrypt(str(site_password))
            self.user_id = user_id



    return EntryBase

@cloud_db.mapped_as_dataclass()
class UserEntryCloud(entry_factory()):
    def __init__(self, site_name, site_username, site_password, user_id=None):
        """Create a new entry in the database"""

        super().__init__(site_name, site_username, site_password, user_id)

        increment_entry_count()


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
            UserEntryCloud(site_name="Facebook.com", site_username="adminusername", site_password="facebook".encode('utf-8')),
        ])
    else:
        app.config['entries'] = db.session.execute(db.select(UserEntryCloud.entry_id)).scalars().all()[-1] + 1
        app.logger.info("administrative: (5a) patient counter updated to %s", app.config['entries'] - 1)
    db.session.commit()