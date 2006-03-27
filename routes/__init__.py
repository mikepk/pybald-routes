"""
Provides common classes and functions most users will want access to.

"""

import threadinglocal, sys

class _RequestConfig(object):
    """
    RequestConfig thread-local singleton
    
    The Routes RequestConfig object is a thread-local singleton that should be initialized by
    the web framework that is utilizing Routes.
    """
    __shared_state = threadinglocal.local()
    
    def __getattr__(self, name):
        return getattr(self.__shared_state, name)

    def __setattr__(self, name, value):
        """
        If the name is environ, load the wsgi envion with load_wsgi_environ
        and set the environ
        """
        if name == 'environ':
            self.load_wsgi_environ(value)
            return self.__shared_state.__setattr__(name, value)
        return self.__shared_state.__setattr__(name, value)
        
    def __delattr__(self, name):
        delattr(self.__shared_state, name)
    
    def load_wsgi_environ(self, environ):
        """
        Load the protocol/server info from the environ and store it.
        Also, match the incoming URL if there's already a mapper, and
        store the resulting match dict in mapper_dict.
        """
        if environ.get('HTTPS'):
            self.__shared_state.protocol = 'https'
        else:
            self.__shared_state.protocol = 'http'
        if hasattr(self, 'mapper'):
            self.mapper.environ = environ
        if 'PATH_INFO' in environ and hasattr(self, 'mapper'):
            mapper = self.mapper
            path = environ['PATH_INFO']
            self.__shared_state.mapper_dict = mapper.match(path)
        host = environ.get('HTTP_HOST') or environ.get('SERVER_NAME')
        self.__shared_state.host = host.split(':')[0]
        if environ.get('SERVER_PORT', 80) != 80:
            self.__shared_state.host += ':' + environ['SERVER_PORT']
    
def request_config(original=False):
    """
    Returns the Routes RequestConfig object.
    
    To get the Routes RequestConfig:
    
    >>> from routes import *
    >>> config = request_config()
    
    The following attributes must be set on the config object every request:
    
    mapper
        mapper should be a Mapper instance thats ready for use
    host
        host is the hostname of the webapp
    protocol
        protocol is the protocol of the current request
    mapper_dict
        mapper_dict should be the dict returned by mapper.match()
    redirect
        redirect should be a function that issues a redirect, 
        and takes a url as the sole argument
    prefix (optional)
        Set if the application is moved under a URL prefix. Prefix
        will be stripped before matching, and prepended on generation
    environ (optional)
        Set to the WSGI environ for automatic prefix support if the
        webapp is underneath a 'SCRIPT_NAME'
        
        Setting the environ will use information in environ to try and
        populate the host/protocol/mapper_dict options if you've already
        set a mapper.
    
    **Using your own requst local**
    
    If you have your own request local object that you'd like to use instead of the default
    thread local provided by Routes, you can configure Routes to use it::
        
        from routes import request_config()
        config = request_config()
        if hasattr(config, 'using_request_local'):
            config.request_local = YourLocalCallable
            config = request_config()
    
    Once you have configured request_config, its advisable you retrieve it again to get the
    object you wanted. The variable you assign to request_local is assumed to be a callable
    that will get the local config object you wish.
    
    This example tests for the presence of the 'using_request_local' attribute which will be
    present if you haven't assigned it yet. This way you can avoid repeat assignments of the
    request specific callable.
    
    Should you want the original object, perhaps to change the callable its using or stop
    this behavior, call request_config(original=True).
    """
    obj = _RequestConfig()
    if hasattr(obj, 'request_local') and original is False:
        return getattr(obj, 'request_local')()
    else:
        obj.using_request_local = False
    return _RequestConfig()
    
from base import Mapper
from util import url_for, redirect_to
__all__=['Mapper', 'url_for', 'redirect_to', 'request_config']
