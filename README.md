Current Issues:
1.	App.config[‘users’] is messing up a lot of things
  a.	Creating new user password entries
    i.	Having issues adding user_id to user entries to link user entry table back to credentials table for proper query to display only the logged in user’s entries
    ii.	Issues handling app.config[‘users’] in both db_classes.py and app.py for addition of new entries
  b.	Cannot create new users 
    i.	App.config[‘users’] messing with this too.
2. I think changing password that was meant to be stored as encrypted data from LargeBinary to a string is causing issues with the encryption.
