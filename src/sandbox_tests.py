'''
Created on Feb 14, 2012

@author: guillaume.aubert@gmail.com

Experimentation and validation of internal mechanisms
'''


import sys
import unittest
import base64


import gmv.gmvault as gmvault
import gmv.gmvault_utils as gmvault_utils
import gmv.imap_utils as imap_utils


def obfuscate_string(a_str):
    """ use base64 to obfuscate a string """
    return base64.b64encode(a_str)

def deobfuscate_string(a_str):
    """ deobfuscate a string """
    return base64.b64decode(a_str)

def read_password_file(a_path):
    """
       Read log:pass from a file in my home
    """
    pass_file = open(a_path)
    line = pass_file.readline()
    (login, passwd) = line.split(":")
    
    return (deobfuscate_string(login.strip()), deobfuscate_string(passwd.strip()))

def delete_db_dir(a_db_dir):
    """
       delete the db directory
    """
    gmvault_utils.delete_all_under(a_db_dir, delete_top_dir = True)


class TestSandbox(unittest.TestCase): #pylint:disable-msg=R0904
    """
       Current Main test class
    """

    def __init__(self, stuff):
        """ constructor """
        super(TestSandbox, self).__init__(stuff)
        
        self.login  = None
        self.passwd = None
        
        self.gmvault_login  = None
        self.gmvault_passwd = None 
    
    def setUp(self): #pylint:disable-msg=C0103
        self.login, self.passwd = read_password_file('/homespace/gaubert/.ssh/passwd')
        
        self.gmvault_login, self.gmvault_passwd = read_password_file('/homespace/gaubert/.ssh/gsync_passwd')
        
        
    def ztest_logger(self):
        """
           Test the logging mechanism
        """
        
        import gmv.log_utils as log_utils
        log_utils.LoggerFactory.setup_cli_app_handler('./gmv.log') 
        
        LOG = log_utils.LoggerFactory.get_logger('gmv') #pylint:disable-msg=C0103
        
        LOG.info("On Info")
        
        LOG.warning("On Warning")
        
        LOG.error("On Error")
        
        LOG.notice("On Notice")
        
        try:
            raise Exception("Exception. This is my exception")
            self.fail("Should never arrive here") #pylint:disable-msg=W0101
        except Exception, err: #pylint:disable-msg=W0101, W0703
            LOG.exception("error,", err)
        
        LOG.critical("On Critical")
        
    def ztest_encrypt_blowfish(self):
        """
           Test encryption with blowfish
        """
        file_path = '../etc/tests/test_few_days_syncer/2384403887202624608.eml.gz'
        
        import gzip
        import gmv.blowfish
        
        #create blowfish cipher
        cipher = gmv.blowfish.Blowfish('VerySeCretKey')
         
        gz_fd = gzip.open(file_path)
        
        content = gz_fd.read()
        
        cipher.initCTR()
        crypted = cipher.encryptCTR(content)
        
        cipher.initCTR()
        decrypted = cipher.decryptCTR(crypted)
        
        self.assertEquals(decrypted, content)
         
    def ztest_copyfile(self):   
        """
           Copyfile
        """
        db_dir = '/tmp/gmail_bk'
        
        gstorer = gmvault.GmailStorer(db_dir)
        
        gstorer.quarantine_email(1254269417797093924L)
        
    def ztest_regexpr(self):
        """
           regexpr for 
        """
        import re
        str = "Subject: Marta Gutierrez commented on her Wall post.\nMessage-ID: <c5b5deee29e373ca42cec75e4ef8384e@www.facebook.com>"
        regexpr = "Subject:\s+(?P<subject>.*)\s+Message-ID:\s+<(?P<msgid>.*)>"
        reg = re.compile(regexpr)
        
        matched = reg.match(str)
        if matched:
            print("Matched")
            print("subject=[%s],messageid=[%s]" % (matched.group('subject'), matched.group('msgid')))
                
    def ztest_dirwalk_test(self):
        """
           Test dirwalk with an existing dir setup
        """
        db_dir = '/home/aubert/Dev/projects/gmvault/src/gmvault-db'
        gstorer = gmvault.GmailStorer(db_dir)
        
        ids = gstorer.get_all_existing_gmail_ids()
        
        for (gmid, dir) in ids:
            print("gmid = %s, dir = %s\n" % (gmid, dir))
        #for key in ids:
        #    print('key = %s, val = %s\n' % (key, ids[key]))
        
    def ztest_decorator(self):
        """
           Test the decorator
        """
        
        class A(object):
            
            def __init__(self, secret):
                self.secret = secret
                
            def connect(self):
                """
                  reconnect
                """
                print("connect")
            
            @imap_utils.retry()
            def get_secret(self, param):
                print(self.secret)
                
        a = A("ZHE ZECRET")
        
        a.get_secret("The PARAM")
        
    def test_retry_mode(self):
        """
           Test that the decorators are functionning properly
        """
        import gmv.imap_utils as imap_utils
        
        class MonkeyIMAPFetcher(imap_utils.GIMAPFetcher):
            
            def __init__(self, host, port, login, credential, readonly_folder = True):
                """
                   Constructor
                """
                super(MonkeyIMAPFetcher, self).__init__( host, port, login, credential, readonly_folder)
                self.connect_nb = 0
                
            def connect(self):
                """
                   connect
                """
                print("In Connect")
            
            @imap_utils.push_email_retry(4)   
            def push_email(self, a_body, a_flags, a_internal_time, a_labels):
                """
                   Throw exceptions
                """
                raise imap_utils.PushEmailError("GIMAPFetcher cannot restore email in %s account." %("myaccount@gmail.com"))
            
        
        imap_fetch = MonkeyIMAPFetcher(host = None, port = None, login = None, credential = None)
        
        imap_fetch.push_email(None, None, None, None)
        

        

def tests():
    """
       main test function
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSandbox)
    unittest.TextTestRunner(verbosity=2).run(suite)
 
if __name__ == '__main__':
    
    tests()