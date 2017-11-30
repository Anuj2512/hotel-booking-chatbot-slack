import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
def sendingemail(toaddress, mailsub, emailbody):
    
    fromaddr = "sannisth.130410116107@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddress
    msg['Subject'] = mailsub
    body = emailbody
    msg.attach(MIMEText(body, 'plain'))

    #server connection and login 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "kaladeep")

    # concatanate whole body into a string
    text = msg.as_string() 

    #sending email and closing the instance
    server.sendmail(fromaddr, toaddress, text)
    server.quit()

if __name__ == '__main__':
    sendingemail (toaddress = "soni.sannisth@gmail.com", #receiver's emailid
                mailsub = "Cali hotel", 
                emailbody = "welcome to fuck all hotel!")


#our emailid and password = sannisth.130410116107@gmail.com, kaladeep