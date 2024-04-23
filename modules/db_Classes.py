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
    username: Mapped[str] = mapped_column(String(50), nullable=False)
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


def user_entry_factory():
    class UserEntryBase:
        """ patient_info table in the database that is
            designed to store patient information
        """

        __tablename__ = "User_Entries"

        user_id: Mapped[int] = mapped_column(ForeignKey("credentials.user_id"), nullable=False)
        site_name: Mapped[str] = mapped_column(String(50), primary_key=True ,unique=True, nullable=False)
        site_username: Mapped[str] = mapped_column(String(50), nullable=False)
        site_password: Mapped[str] = mapped_column(LargeBinary, nullable=False)

        def iterable(self):
            """ returns the object's member variables as a list that
                can be iterated through
            """
            return [self.site_name,
                    self.site_username,
                    self.site_password,
                    ]

        def decrypt(self):
            """ decrypts the encrypted fields of the object
            """
            self.site_password = decrypt(self.site_password)

        def __init__(self, site_name, site_username, site_password):
            """ base class ctor to create a user entry in the database.
                inherited by the database classes. It
                stores an encrypted password from the user's
                data and stores it in the database.
                the passwords are encrypted before being stored in
                the database.
            """

            self.user_id = session['id']
            self.site_name = site_name.title()
            self.site_username = site_username.title()
            self.site_password = encrypt(str(site_password))  # encrypt the password


    return UserEntryBase


@cloud_db.mapped_as_dataclass()
class UserEntryCloud(user_entry_factory()):
    def __init__(self, site_name, site_username, site_password):
        """ create a user in the cloud database. """

        # use the base class ctor to create a patient
        super().__init__(site_name, site_username, site_password)



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