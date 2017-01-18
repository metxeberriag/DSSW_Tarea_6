#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from google.appengine.ext.webapp \
    import template
from webapp2_extras import sessions
import session_module
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib

class Image(ndb.Model):
    user = ndb.StringProperty()
    public = ndb.BooleanProperty()
    blobkey = ndb.BlobKeyProperty()

class UploadHandler(session_module.BaseSessionHandler, blobstore_handlers.BlobstoreUploadHandler):
    
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
            self.redirect('/menu')

        else:
            values = {'messageError' : 'Tienes que logearte!'}
            self.response.out.write(template.render('html/login.html', values))

class ViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        fotos = blobstore.BlobInfo.all()
        for foto in fotos:
            self.response.out.write('<td><img src="menu/serve/%s"></img></td>' % foto.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
     def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class AlbumHandler(session_module.BaseSessionHandler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self):

        if 'user' in self.session:
            private_images = Image.query().filter(Image.public == False).filter(Image.user == self.session.get('email'))

            private = ""
            priv = 1
            for img in private_images:
                private += '<div class="responsive"><div class="img"><img onmouseover="preview.src=img{0}.src" name="img{0}" src="/menu/serve/{1}" alt="" /></div></div>'.format(priv,img.blobkey)
                priv += 1

            public_images = Image.query().filter(Image.public == True).filter(Image.user == self.session.get('email'))

            public = ""
            pub = 1
            for img in public_images:
                public += '<div class="responsive"><div class="img"><img onmouseover="preview.src=img{0}.src" name="img{0}" src="/menu/serve/{1}" alt="" /></div></div>'.format(pub,img.blobkey)
                pub += 1

            values = {}
            self.response.out.write(template.render('html/album.html', values))
            self.response.out.write(private)
            self.response.out.write(public)
            self.response.out.write(
                '''</tr></table></body></html>'''
            )

        else:
            public_images = Image.query().filter(Image.public == True).filter(Image.user == self.session.get('email'))
            public = ""
            pub = 1
            for img in public_images:
                public += '<div class="responsive"><div class="img"><img onmouseover="preview.src=img{0}.src" name="img{0}" src="/menu/serve/{1}" alt="" /></div></div>'.format(pub,img.blobkey)
                pub += 1

            values = {}
            self.response.out.write(template.render('html/album.html', values))
            self.response.out.write(public)
            self.response.out.write(
                '''</tr></table></body></html>'''
            )


app = webapp2.WSGIApplication([
    ('/menu/album', AlbumHandler),
    ('/menu/upload', UploadHandler),
    ('/menu/download', ViewHandler),
    ('/menu/serve/([^/]+)?', ServeHandler)
], config = session_module.config, debug=True)