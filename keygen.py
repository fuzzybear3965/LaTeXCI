import argparse
from cryptography.fernet import Fernet

parser = argparse.ArgumentParser(description='Generate encrypted API key \
        to be used with the WebHook URL query.')
parser.add_argument('--symkey',
        help='Symmtric key (only include if you want to decrypt your generated, \
                encrypted API key.')
parser.add_argument('apikey',
        help='API key that needs to be encrypted.')

args = parser.parse_args()
if args.symkey is None:
    symkey = Fernet.generate_key()
    cipher_suite = Fernet(symkey)
    print
    print "API key: " + cipher_suite.encrypt(args.apikey)
    print
    print "Type of symmetric key: " 
    print type(cipher_suite.encrypt(args.apikey))
    print
    print "Symmetric key: " + symkey
    print
    print "Type of symmetric key: " 
    print type(symkey)
    print
    print "Now, store both of these quantities in app.cgf, immediately in the following form."
    print
    print "apikey=<someApiKey>"
    print "symkey=<someSymmetricKey>"
else:
    symkey = args.symkey
    cipher_suite = Fernet(symkey)
    print
    print "Your API key (decrypted) is: " + cipher_suite.decrypt(args.apikey)
    print
