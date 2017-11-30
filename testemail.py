import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
def sendingemail(toaddr, emailsub, emailbody):
    
    fromaddr = "sannisth.130410116107@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = "Hotel California"
    msg['To'] = toaddr
    msg['Subject'] = emailsub
    body = emailbody
    msg.attach(MIMEText(body, 'plain'))

    #server connection and login 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "kaladeep")

    # concatanate whole body into a string
    text = msg.as_string() 

    #sending email and closing the instance
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

if __name__ == '__main__':
    sendingemail ("soni.sannisth@gmail.com", "Regarding room booking/cancellation", "welcome to fuck all hotel!")


#our emailid and password = sannisth.130410116107@gmail.com, kaladeep
