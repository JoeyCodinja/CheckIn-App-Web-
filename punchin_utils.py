import re

class Utils(object):
    def __init__(self):
        pass 
    
    @staticmethod
    def match_email(query):
        #Regex matching gmail account emails
        email_regex = re.compile(r"\w@gmail.com", re.IGNORECASE)
        if (isinstance(query, str) or isinstance(query, unicode)):
            return email_regex.match(query) is not None
    
        return False

    
    @staticmethod
    def match_pass_id(query):
        # Regex matching pass ids; both staff and intern
        import re
        pass_id_regex =  re.compile(r"(?P<intern_id>\d{5}p)|(?P<staff_id>\d{9})", re.IGNORECASE)
        if (isinstance(query, str) or isinstance(query, unicode)):
            result = pass_id_regex.match(query)
            if result.group('intern_id') is not None:
                return True
            elif result.group('staff_id') is not None:
                return True
            else:
                return False
        
        return False
    
    @staticmethod 
    def display_time():
        from datetime import datetime, timedelta
        jamaica_time_offset = timedelta(hours=5)
        display_datetime = datetime.today() - jamaica_time_offset
        return display_datetime
    
    @staticmethod
    def escape_email_id(email):
        invalid_characters = r'[.$\[\]#/]'
        search_obj = re.search(invalid_characters, email) 
        
        while search_obj is not None:
            invalid_character = email[search_obj.start():search_obj.end()]
            print invalid_character
            email = email.replace(invalid_character, '!%03d!' % ord(invalid_character), 1)
            search_obj = re.search(invalid_characters, email)
        
        print email
        
        return email
        
    @staticmethod
    def parse_email_id(escaped_email):
        escaped_character_match = r'!(\d{3})!'
        search_obj = re.search(escaped_character_match, escaped_email)
        
        while search_obj is not None:
           replace_chr = chr(int(search_obj.group(1)))
           escaped_chr = escaped_email[search_obj.start():search_obj.end()]
           escaped_email = escaped_email.replace(escaped_chr, replace_chr)
           search_obj = re.search(escaped_character_match, escaped_email)
        
        print escaped_email 
        
        return escaped_email
    