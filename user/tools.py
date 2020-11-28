import random, secrets

# Upload paths
def pic_path(instance, filename):
    """Generates the path where user profile picture will be saved."""

    return "images/users/%s.%s"%(instance.user, filename.split('.')[-1])




# Random URL safe tokens for email confirmation
def make_token():
    """Generates and returns random token code and URL safe token URL."""
    code = random.randint(100000, 600000)
    token = secrets.token_urlsafe(40)
    
    return {"code": code, "token": token}


# Crafts confirmation email to be used in verifying user email address.
def confirm_mail(email, username):
    """Constructs confirmation email message to be sent to New User upon 
    registration to confirm User Email address is valid.
    
    All parameters are required.
    
    Upon success, returns token code."""
    token = make_token()
    
    txt = """Thank you for registering an account with Easy Chat. \n
    This email address ({email}) was used to register a new account at 
    https://easychat.pythonanywhere.com/ Easy Chat.\n
    Please click this link to confirm your email to validate your registration
    http://easychat.pythonanywhere.com/u/verify/{username}/{token}/{code}/Confirm \n
    Alternatively, if the link above is not clickable, you can visit; 
    https://easychat.pythonanywhere.com/u/verify/{username}/ 
    and enter {code} as your verification code.\n

    Note: This link expires automatically in 48hrs and becomes invalid after 
    the specified period.\n
    If you received this mail in error, please disregard it and we will never 
    contact you again.\n
    This is an automatically generated email and hence should not be replied.\n
    If you need further information, please visit; 
    https://easychat.pythonanywhere.com/contact%20us/ or better still send a 
    mail to isfestus@gmail.com.\n\n
    Kind regards,\n
    Easy Chat.\n
    """.format(username=username, email=email, token=token["token"], 
            code=token["code"])


    html = """This email address ({email}) was used to register a new account 
    at <a href="https://easychat.pythonanywhere.com/">Easy Chat</a>.<br>
    <p>Please click below link to confirm your registration; <br> 
    <a href="http://easychat.pythonanywhere.com/u/verify/{username}/{token}/{code}/">
    Confirm Email</a> </p>
    <p>Alternatively, if the link above is not clickable, you can visit; <br> 
    https://easychat.pythonanywhere.com/u/verify/{username}/ 
    and enter <b>{code}</b> as your verification code. </p>
    <p><b>Note:</b> This link expires automatically in 48hrs and becomes 
    invalid after the specified period.</p>
    <p>If you received this mail in error, please disregard it and we will 
    never contact you again.</p>
    <p>This is an automatically generated email and hence should not be 
    replied.<br> If you need further information, please visit; <br> 
    https://easychat.pythonanywhere.com/contact%20us/ or better still 
    send a mail to isfestus@gmail.com.</p>
    <p>Kind regards,<br>
    Easy Chat.</p>
    """.format(username=username, email=email, token=token["token"], 
            code=token["code"])
        
    return (txt, html)

    

# Get email domain/server address
def get_email_domain(email):
    """Generates email domain from given email address."""

    return "www."+email.split("@")[-1]
