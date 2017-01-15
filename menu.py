#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import re
from google.appengine.ext.webapp \
    import template
from webapp2_extras import sessions
import session_module
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

class Image(ndb.Model):
    user = ndb.StringProperty()
    public = ndb.BooleanProperty()
    blob_key = ndb.BlobKeyProperty()

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        if 'user' in self.session:
            upload_url = blobstore.create_upload_url('/menu/upload')
            values = {'url': upload_url}
            self.response.out.write(template.render('html/subirFoto.html', values))
        else:
            values = {'messageError' : 'Tienes que logearte!'}
            self.response.out.write(template.render('html/login.html', values))
    
    def post(self):
        if 'user' in self.session:
            upload_files = self.get_uploads('file')
            blob_info = upload_files[0] # guardo la imagen en el BlobStore
            img = Image(user=self.session.get('email'),  public=self.request.get("access")=="public", blobkey=blob_info.key())
            img.put() #guardo el objeto Image

class ViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        fotos= blobstore.BlobInfo.all()
        for foto in fotos:
        self.response.out.write('<img src="serve/%s"></image></td>' % foto.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
     def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


app = webapp2.WSGIApplication([
    ('/menu/upload', UploadHandler),
    ('/album'), ViewHandler),
    ('/serve/([^/]+)?', ServerHandler)
], config = session_module.config, debug=True)