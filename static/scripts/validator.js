function validate() {
    var pass1 = $('#password1').val();
    var pass2 = $('#password2').val();
    if (pass1 != pass2 || pass1=="" || pass2=="") {
        alert("Las contraseñas no son las mismas!");
        return false;
    }
}

function validarEmailAjax() {

  var XMLHttpRequestObject = new XMLHttpRequest();
  var email = document.getElementById("email");
  var emailV = "?emailA=" + email.value;
  var respuesta;
  var error = true;

  if(XMLHttpRequestObject)
  {
    XMLHttpRequestObject.onreadystatechange = function()
    {
      if (XMLHttpRequestObject.readyState==4)
      {
        respuesta = XMLHttpRequestObject.responseText;
        if (respuesta == ""){
          respuesta = "Email correcto!";
          error = false;
        }
        document.getElementById("errorEmail").innerHTML = (respuesta);
        if (error) {
        	document.getElementById("errorEmail").style.color= "red";
        } else {
        	document.getElementById("errorEmail").style.color= "green";
        }
      }
    }
  }
	XMLHttpRequestObject.open("get", "/validate" + emailV, true );
    XMLHttpRequestObject.send(null);
  }

