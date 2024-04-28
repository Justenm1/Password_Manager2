This is a web-base multi-user password manager that implements a few security features to allow users to security store their password from other sites. It uses Flask as a web frame and SQLAlchemy to handle database interactions with the server. Python is the primary language, but it also uses HTML and JavaScript to implement a easy to use front-end for the user.
Security measures include:
•	Password strength requirements
  o	Strong password generator to aid in this requirement for user experience
•	User profile password hashing
•	SQLAlchemy proofing against SQL injection attacks
•	User entry password AES256 encryption
•	Role-based access control
•	User authentication
