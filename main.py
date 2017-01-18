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
import base64


class MainHandler(session_module.BaseSessionHandler):
    def get(self):
        sessionMessage = ""
        counterMessage = ""
        self.session['logeado'] = False
        attr = {
            'sessionMessage': sessionMessage,
            'counterMessage': counterMessage
        }

        self.response.out.write(template.render('html/main.html', attr))

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    created= ndb.DateTimeProperty(auto_now_add=True)
    bloqueado = ndb.BooleanProperty(default=False)

class RegisterHandler(webapp2.RequestHandler):
    
    def get(self):
        self.response.write(template.render('html/registro.html', {}))
    
    def post(self):
        errorUsername = ""
        errorEmail = ""
        errorPassword1 = ""
        errorPassword2 = ""
        username = self.request.get('username')
        password1 = self.request.get('password1')
        password2 = self.request.get('password2')
        email = self.request.get('email')
        valido = True
        USER_RE = re.compile(r"^[a-zA-Z0-9]+([a-zA-Z0-9](_|-| )[a-zA-Z0-9])*[a-zA-Z0-9]+$")
        PASSWORD_RE = re.compile(r"^[a-zA-Z0-9]+([a-zA-Z0-9](_|-| )[a-zA-Z0-9])*[a-zA-Z0-9]+$")
        EMAIL_RE = re.compile(r"^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$")
        
        if not USER_RE.match(username):
            errorUsername = "El username no es correcto!"
            valido = False
        
        if not PASSWORD_RE.match(password1):
            errorPassword1 = "El password no es correcto!"
            valido = False
        
        if not PASSWORD_RE.match(password2):
            errorPassword2 = "El password no es correcto!"
            valido = False
        
        if not password1==password2:
            errorPassword2 = "Los password no coinciden!"
            valido = False

        if not EMAIL_RE.match(email):
            errorEmail = "El email no es correcto!"
            valido = False
        
        if not valido:
            attr = {
                'username' : username,
                'password1' : password1,
                'password2' : password2,
                'email' : email,
                'errorUsername': errorUsername,
                'errorEmail' : errorEmail,
                'errorPassword1' : errorPassword1,
                'errorPassword2' : errorPassword2
            }

            self.response.write(template.render('html/registroNoValido.html', attr))

        if valido:
            correctoEmail = False
            correctoUser = False
            errorDatos = ""
            nusers = User.query(User.username==username).count()
            nemails = User.query(User.email==email).count()
            if nemails==1:
                # está en el modelo
                correctoEmail = False
                errorDatos = "email"
            else:
                # NO está en el modelo
                correctoEmail = True
            
            if nusers==1:
                # está en el modelo
                correctoUser = False
                if correctoEmail:
                    errorDatos += "nombre de usuario"
                else:
                    errorDatos += " y nombre de usuario"
            else:
                # NO está en el modelo
                correctoUser = True
            
            if correctoUser and correctoEmail:
                datos = User()
                datos.username = self.request.get('username')
                datos.email = self.request.get('email')
                datos.password = self.request.get('password1')
                datos.put()
                attr = { 
                    'username' : username,
                    'email' : email
                }
                self.response.write(template.render('html/registroCorrecto.html', attr))

            else:
                attr = { 'errorDatos' : errorDatos }
                self.response.write(template.render('html/registroError.html', attr))
                      
class ValidatorHandler(webapp2.RequestHandler):
    def get (self) :
        EMAIL_RE = re.compile(r"^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$")
        errorEmail= ""
        email = self.request.get('emailA')
        nemails = User.query(User.email==email).count()

        if not EMAIL_RE.match(email):
            errorEmail = "El email no es correcto!"

        if (nemails>=1):
            errorEmail= "Ese e-mail ya esta registrado"

        self.response.write(errorEmail)

class LoginHandler(session_module.BaseSessionHandler):
    def get(self):
        values = {}
        self.response.out.write(template.render('html/login.html', values))
    
    def post(self):
        if 'user' in self.session:
            self.redirect('/menu')
        else:
            password = self.request.get('password')
            email = self.request.get('email')

            messageError = ""
            error = False
            existe = True
            correcto = True

            PASSWORD_RE = re.compile(r"^[a-zA-Z0-9]+([a-zA-Z0-9](_|-| )[a-zA-Z0-9])*[a-zA-Z0-9]+$")
            EMAIL_RE = re.compile(r"^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$")

            if not PASSWORD_RE.match(password):
                error = True

            if not EMAIL_RE.match(email):
                error = True

            usuarios = User.query().filter(User.email==email)

            if usuarios.count()==0:
                existe = False

            if existe and not error:
                if not 'login_tries' in self.session:
                    self.session['login_tries'] = 0
                    correcto = True
                elif not (self.session['login_tries'] < 3):
                    correcto = False
                    self.session['login_tries'] = 0

                if correcto:
                    comprobarPassword = User.query().filter(User.email==email).filter(User.password==password).get()
                    if comprobarPassword:
                        if comprobarPassword.bloqueado:
                            messageError = "Ese usuario esta bloqueado!"
                            password = ""
                            values = {'messageError': messageError, 'email': email, 'password': password}
                            self.response.out.write(template.render('html/login.html', values))
                        else:
                            self.session['user'] = email
                            self.session['login_tries'] = 0
                            self.redirect('/menu')

                    elif usuarios.get().bloqueado:
                        messageError = "Ese usuario esta bloqueado!"
                        password = ""
                        self.session['login_tries'] = 0
                        values = {'messageError': messageError, 'email': email, 'password': password}
                        self.response.out.write(template.render('html/login.html', values))
                    else:
                        intentos = 2-self.session['login_tries']
                        messageError = "El email o la contrasena son incorrectos! Tienes "+str(intentos)+" intentos más."
                        self.session['login_tries'] = self.session['login_tries']+1
                        password = ""
                        values = {'messageError': messageError, 'email': email, 'password': password}
                        self.response.out.write(template.render('html/login.html', values))
                else:
                    messageError = "Se ha bloqueado la cuenta!"
                    usuario2 = User.query().filter(User.email==email).get()
                    usuario2.bloqueado = True
                    usuario2.put()
                    values = {'messageError': messageError}
                    self.response.out.write(template.render('html/login.html', values))    
            else:
                messageError = "El email o la contrasena son incorrectos!" 
                values = {'messageError': messageError, 'email': email, 'password': password}
                self.response.out.write(template.render('html/login.html', values))

                

class MenuHandler(session_module.BaseSessionHandler):
    def get(self):
        if 'user' in self.session:
            usuarios = ndb.gql("SELECT * FROM User WHERE email=:1", self.session['user'])
            username = usuarios.get().username
            values = {'user' : username}
            self.response.out.write(template.render('html/menu.html', values))
        else:
            self.redirect('/')

class LogoutHandler(session_module.BaseSessionHandler):
    def get(self):
        if(self.session['user']):
            del self.session['user']
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/logoutSession', LogoutHandler),
    ('/menu', MenuHandler),
    ('/', MainHandler),
    ('/registro', RegisterHandler),
    ('/login', LoginHandler),
    ('/validate', ValidatorHandler),
], config = session_module.config, debug=True)