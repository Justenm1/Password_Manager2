from flask import session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from modules.globals import app


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

    # check if the password needs to be rehashed
    # this returns true if the instance's parameters change
    if argon2.check_needs_rehash(pw_hash):
        app.logger.info('WARNING: password needs to be rehashed')

    try:
        return argon2.verify(pw_hash, password)
    except VerifyMismatchError:
        return False


def logged_in():
    """ Check if the user is logged in
    """
    return 'logged_in' in session


def encrypt(data):
    """ encrypt data using AES in CBC mode with a 16 byte
        initialization vector. returns the ciphertext
    """
    key = str.encode('informationsecurinformationsecur')  # 32 bytes key
    dataforpadding = data.encode('utf-8')
    iv = get_random_bytes(16)
    print(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    print(cipher.iv)
    cipher_text = cipher.encrypt(pad(dataforpadding, AES.block_size))
    print(cipher_text)
    return cipher_text, iv


def decrypt(cipher_text, iv):
    """ decrypt data using AES in CBC mode with a 16 byte
        initialization vector. returns the cleartext
    """

    # use the flask secret for the secret key
    key = str.encode('informationsecurinformationsecur')

    decrypt_cipher = AES.new(key, AES.MODE_CBC, iv)

    plain_text = unpad(decrypt_cipher.decrypt(cipher_text), AES.block_size)

    # return the deciphered text as a utf-8 string
    return plain_text

def decryptentry(cipher_text, iv):
    """ decrypt data using AES in CBC mode with a 16 byte
        initialization vector. returns the cleartext
    """

    # use the flask secret for the secret key
    key = str.encode('informationsecurinformationsecur')
    texttodecrypt = cipher_text.encode('utf-8')
    byteiv = iv.encode('utf-8')
    decrypt_cipher = AES.new(key, AES.MODE_CBC, byteiv)

    encoded_text = unpad(decrypt_cipher.decrypt(texttodecrypt), AES.block_size)
    plain_text = str(encoded_text, 'utf-8')
    # return the deciphered text as an utf-8 string
    return plain_text
