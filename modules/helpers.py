from flask import session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from modules.globals import app
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def create_session(user_id, user, role):
    """ Create a session for the user
    """
    session['logged_in'] = True
    session['id'] = user_id
    session['username'] = user
    session['role'] = role


def hash_pw(password):
    """ Hash the user's password using argon2-cffi
    """
    # create an argon2 hasher instance
    # by default it uses a 16 byte salt
    argon2 = PasswordHasher()

    # returns a 16 byte hash value for the password
    # encoded with the salt and other parameters
    return str.encode(argon2.hash(password))


def verify_pw(pw_hash, password):

    # create an argon2 hasher instance
    argon2 = PasswordHasher()

    try:
        return argon2.verify(pw_hash, password)
    except VerifyMismatchError:
        return False


def logged_in():
    """ Check if the user is logged in
    """
    return 'logged_in' in session


def increment_entry_count():
    # increment global patients counter
    app.config['entries'] += 1


def mypad(data, length=32, add_code=True):
    """ pad data to a multiple of the specified length.
            if add_code is true, the pad length is encoded
            with the data. returns the padded data
        """

    # calculate required length of padding
    k = len(data)
    if k % length > 0:
        pad_length = (k // length + 1) * length - k
    else:
        pad_length = 0

    # add the padding to the data
    data += b"#" * pad_length

    if add_code:
        # encode the pad length with the data
        pad_code = bytes(chr(ord("A") + pad_length).encode("utf-8"))
        data = data + b"*" * (length - 1) + pad_code

    return data


def encrypt(data, iv=None):
    """ encrypt data using AES in CBC mode with a 16 byte
        initialization vector. returns the ciphertext
    """
    from modules.secrets import key  # 32 bytes key

    # format the iv to a 16 byte string
    if iv:
        iv = mypad(str(iv).encode('utf-8'), 16, False)
    else:
        iv = mypad(str(app.config['entries']).encode('utf-8'), 16, False)

    # create a cipher object using the key and iv
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    # prepare the cleartext for encryption
    cleartext = mypad(data.encode('utf-8'), 16)

    # create an encryptor object
    encryptor = cipher.encryptor()

    # encrypt the padded cleartext
    return encryptor.update(cleartext) + encryptor.finalize()


def decrypt(data, iv):
    """ decrypt data using AES in CBC mode with a 16 byte
        initialization vector. returns the cleartext
    """

    # use the flask secret for the secret key
    from modules.secrets import key

    if session['role'] == 'H':
        return data
    else:
        # create the iv from the patient tuple's patient_id
        iv = mypad(str(iv).encode('utf-8'), 16, False)

        # create a cipher object using the key and iv
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

        # create a decryptor object
        decryptor = cipher.decryptor()

        # decrypt the ciphertext
        decipher_text = decryptor.update(data) + decryptor.finalize()

        # remove the pad code block from the deciphered text
        pad_block = decipher_text[-16:]  # get the pad code block
        clear_text = decipher_text[:-16]  # remove the pad code block

        # remove the padding from the deciphered text using the pad code
        pad_code = pad_block[-1] - ord("A")  # get the pad code
        clear_text = clear_text[:-pad_code]  # remove the padding

        # return the deciphered text as a utf-8 string
        return clear_text.decode("utf-8")