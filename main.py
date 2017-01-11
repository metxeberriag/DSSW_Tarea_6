#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import webapp2
import re
from google.appengine.ext import ndb

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    created= ndb.DateTimeProperty(auto_now_add=True)

class RegisterHandler(webapp2.RequestHandler):
    
    def get(self):
        self.response.write('''
        <html>
            <head>
                <link rel="stylesheet" href="styles/estilo.css">
                <script src="scripts/validator.js"></script>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
            </head>
            <body>
                <h1 class="register-title">DSSW - TAREA 4</h1>
                <form method="post" id="login" class="register">
                    <table>
                        <tr>
                            <td class="label"> Nombre de usuario </td>
                            <td> <input type="text" name="username" id="username" value="" placeholder="Tu nombre..." class="register-input"> </td>
                            <td> <span id="errorUsername" style="color:red"></span> </td>
                        </tr>
                        <tr>
                            <td class="label"> Password </td>
                            <td> <input type="password" name="password1" id="password1" value="" placeholder="Tu contraseña..." class="register-input"></td>
                            <td> <span id="errorPassword1" style="color:red"></span> </td>
                        </tr>
                        <tr>
                            <td class="label">Repetir Password </td>
                            <td> <input type="password" name="password2" id="password2" value="" placeholder="El mismo de antes" class="register-input"> </td>
                            <td> <span id="errorPassword" style="color:red"></span> </td>
                        </tr>
                        <tr>
                            <td class="label"> Email </td>
                            <td> <input type="text" onBlur="validarEmailAjax()" name="email" value="" id="email" placeholder="Tu email..." class="register-input"> </td>
                            <td> <span id="errorEmail"></span></td>
                        </tr>
                    </table>
                    <input type="submit" id="enviar" class="register-button">
                </form>
            </body>
            </html>''')
    
    def post(self):
        errorUsername = ""
        errorEmail = ""
        errorPassword = ""
        errorPassword1 = ""
        valido = True
        USER_RE = re.compile(r"^[a-zA-Z0-9]+([a-zA-Z0-9](_|-| )[a-zA-Z0-9])*[a-zA-Z0-9]+$")
        PASSWORD_RE = re.compile(r"^[a-zA-Z0-9]+([a-zA-Z0-9](_|-| )[a-zA-Z0-9])*[a-zA-Z0-9]+$")
        EMAIL_RE = re.compile(r"^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$")
        if not USER_RE.match(self.request.get('username')):
            errorUsername = "El username no es correcto!"
            valido = False
        
        if not PASSWORD_RE.match(self.request.get('password1')):
            errorPassword1 = "El password no es correcto!"
            valido = False
        
        if not PASSWORD_RE.match(self.request.get('password2')):
            errorPassword = "El password no es correcto!"
            valido = False
        
        if not self.request.get('password1')==self.request.get('password2'):
            errorPassword = "Los password no coinciden!"
            valido = False

        if not EMAIL_RE.match(self.request.get('email')):
            errorEmail = "El email no es correcto!"
            valido = False
        
        if not valido:
            self.response.write('''
        <html>
            <head>
                <link rel="stylesheet" href="styles/estilo.css">
                <script src="scripts/validator.js"></script>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
            </head>
            <body>
                <h1 class="register-title">DSSW - TAREA 4</h1>
                <form method="post" id="login" class="register">
                    <table>
                        <tr>
                            <td class="label"> Nombre de usuario </td>
                            <td> <input type="text" name="username" id="username" value="" placeholder="Tu nombre..." class="register-input"> </td>
                            <td> <span id="errorUsername" style="color:red">'''+errorUsername+'''</span> </td>
                        </tr>
                        <tr>
                            <td class="label"> Password </td>
                            <td> <input type="password" name="password1" id="password1" value="" placeholder="Tu contraseña..." class="register-input"></td>
                            <td> <span id="errorPassword1" style="color:red">'''+errorPassword1+''' </td>
                        </tr>
                        <tr>
                            <td class="label">Repetir Password </td>
                            <td> <input type="password" name="password2" id="password2" value="" placeholder="El mismo de antes" class="register-input"> </td>
                            <td> <span id="errorPassword" style="color:red">'''+errorPassword+'''</span> </td>
                        </tr>
                        <tr>
                            <td class="label"> Email </td>
                            <td> <input type="text" name="email" value="" id="email" placeholder="Tu email..." class="register-input" onBlur="validarEmailAjax()"> </td>
                            <td> <span id="errorEmail" style="color:red">'''+errorEmail+'''</span> </td>
                        </tr>
                    </table>
                    <input type="submit" id="enviar" class="register-button">
                </form>
            </body>
            </html>''')

        if valido:
            correctoEmail = False
            correctoUser = False
            errorDatos = ""
            nusers = User.query(User.username==self.request.get('username')).count()
            nemails = User.query(User.email==self.request.get('email')).count()
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
                self.response.write('''
                <html>
                    <head>
                        <link rel="stylesheet" href="styles/estilo.css">
                    </head>
                    <body>
                        <h1 class="register-title">DSSW - TAREA 4</h1>
                        <form class="register">
                        <h2>El registro se ha completado correctamente!</h2><br>'''
                                + "<p>Hola " + self.request.get('username')+'''!</p><br>'''
                                + "<p>Tu email es " + self.request.get('email')+'''</p><br><br>
                            <a href="/registro" class="register-button">Volver</a>
                        </form>
                    </body>
                </html>''')
            else:
                self.response.write('''
                    <html>
                    <head>
                    <link rel="stylesheet" href="styles/estilo.css">
                    <script src="scripts/validator.js"></script>
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
                    </head>
                    <body>
                    <h1 class="register-title">DSSW - TAREA 4</h1>
                    <form method="post" id="login" class="register">
                    <table>
                    <tr>
                    <td class="label"> Nombre de usuario </td>
                    <td> <input type="text" name="username" id="username" value="" placeholder="Tu nombre..." class="register-input"> </td>
                    <td> <span id="errorUsername" style="color:red"></span> </td>
                    </tr>
                    <tr>
                    <td class="label"> Password </td>
                    <td> <input type="password" name="password" id="password1" value="" placeholder="Tu contraseña..." class="register-input"></td>
                    <td> <span id="errorPassword1" style="color:red"></span> </td>
                    </tr>
                    <tr>
                    <td class="label">Repetir Password </td>
                    <td> <input type="password" name="password2" id="password2" value="" placeholder="El mismo de antes" class="register-input"> </td>
                    <td> <span id="errorPassword" style="color:red"></span> </td>
                    </tr>
                    <tr>
                    <td class="label"> Email </td>
                    <td> <input type="text" name="email" value="" id="email" placeholder="Tu email..." class="register-input" onBlur="validarEmailAjax()"> </td>
                    <td> <span id="errorEmail" style="color:red"></span> </td>
                    </tr>
                    </table>
                    <input type="submit" id="enviar" class="register-button">
                    <span id="errorDatos" style="color:red"> Ese '''+errorDatos+''' ya existe!</span>
                    </form>
                    </body>
                    </html>''')
                      
class ValidatorHandler(webapp2.RequestHandler):
    def get (self) :
        EMAIL_RE = re.compile(r"^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$")
        error = False
        errorEmail= ""
        email = self.request.get('emailA')
        nemails = User.query(User.email==email).count()

        if not EMAIL_RE.match(email):
            error = True
            errorEmail = "El email no es correcto!"

        if (nemails>=1):
            error = True
            errorEmail= "Ese e-mail ya esta registrado"

        self.response.write(errorEmail)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('''
            <html>
                <body>
                    <head>
                        <link rel="stylesheet" href="/styles/main_eu.css">
                    </head>
                    <p>Kaixo Mundua!</p>
                    <img src="/images/kaixo.gif" />
                </body>
            </html>''')

class EsHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('''
            <html>
                <body>
                    <head>
                        <link rel="stylesheet" href="/styles/main_es.css">
                    </head>
                    <p>Hola Mundo!</p>
                    <img src="/images/kaixo.gif" />
                </body>
            </html>''')

class EnHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('''
            <html>
                <body>
                    <head>
                        <link rel="stylesheet" href="/styles/main_en.css">
                    </head>
                    <p>Hello World!</p>
                    <img src="/images/kaixo.gif" />
                </body>
            </html>''')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/es', EsHandler),
    ('/en', EnHandler),
    ('/registro', RegisterHandler),
    ('/validate', ValidatorHandler),
], debug=True)

		