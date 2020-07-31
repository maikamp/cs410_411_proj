# should be a potential configuration file I saw an example an added it
# but not fully sure why to use this one
import os


class Config(object):
    TESTING = False
    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'docx', 'doc', 'odt', 'htm', 'html', 'md', 'py', 'java', 'cpp'}
    CONVERTIBLE_EXTENSIONS = {'doc', 'docx', 'odt', 'htm', 'html'}