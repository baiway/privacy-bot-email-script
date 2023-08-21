import json
import pandas as pd
import smtplib
from email.message import EmailMessage
import time
from datetime import datetime
from getpass import getpass

def generate_html(userdata, submap, template="template.html") -> str:
    """Generates HTML content of email.
    """
    # Build user's data that will be sent to broker
    ordered_list = ""
    for attribute, data in userdata.items():
        if submap[attribute] == True:
            if isinstance(data, list):
                data = ", ".join(data)
            ordered_list += f"      <li> {attribute}: {data} </li>\n"

    # Write the message body using user_pii
    with open("template.html", "r") as f:
        template = f.read()

    list_start = template.find("<ol>") + len("<ol>")
    list_end = template.find("</ol>")
    sign_off = template.find("Kind regards<br/>") + len("Kind regards<br/>")
    html = (template[:list_start] + "\n" + ordered_list + "    " + 
            template[list_end:sign_off] + "\n    " + userdata["firstname"] + 
            " " + userdata["lastname"] + template[sign_off:])
    
    return html

def generate_plain_text(userdata, submap, template="template.txt") -> str:
    """Generates alternative plain text content of email.
    """
    # Build user's data that will be sent to broker
    unordered_list = ""
    for attribute, data in userdata.items():
        if submap[attribute] == True:
            if isinstance(data, list):
                data = ", ".join(data)
            unordered_list += f"- {attribute}: {data} \n"

    # Generate the message body using userdata
    with open("template.txt", "r") as f:
        template = f.read()

    list_start = template.find("My details are:") + len("My details are:")
    list_end = template.find("In the case that")
    sign_off = template.find("Kind regards") + len("Kind regards")
    text = (template[:list_start] + "\n" + unordered_list + "\n" +
            template[list_end:sign_off] + "\n" + userdata["firstname"] + " " 
            + userdata["lastname"] + template[sign_off:])
    
    return text

def csv_to_map(service_list, subset="top_choice") -> dict:
    """Converts CSV of services to a dictionary of services with the service
     names as keys. Code adapted from the 
     [PrivacyBot](https://github.com/privacybot-berkeley/privacybot) 
     GitHub 
     repository.

     Example usage
     -------
     >>> services = csv_to_map(service_list="services_list.csv", 
                                subset="all")
     >>> services["AcmeData"]["privacy_dept_contact_email"]
     privacy@acmedata.com
     >>> services["AcmeData"]["category"]
     data broker
    """

    try:
        n_columns = len(pd.read_csv(service_list, nrows=0).columns)
        # ignore last five columns in service_list. These are: device_ad_id, 
        # twitter_handle, link_to_profile, gov_photo_id, used_by_le, notes.
        columns_to_load = list(range(n_columns - 5))
        df = pd.read_csv(service_list, usecols=columns_to_load)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    subsets = ["all", "people search", "top_choice"]
    if subset not in subsets:
        raise ValueError(f"Unknown subset: {subset}. \
                          Available subsets are: {', '.join(subsets)}.")
    else:
        print(f"Sending to {subset} services.")

    all_services = df.set_index("service_name_cleaned").to_dict(orient='index')

    if subset == "all":
        return all_services
    elif subset == "people search":
        return {k: v for k, v in all_services.items() 
                if v['category'] == "people search"}
    else:
        return {k: v for k, v in all_services.items() 
                if v["top_choice"] == "YES"}         

def send_emails(services_map, username, password, userdata="userdata.json", 
                omit=None):
    successful = {}
    unsuccessful = {}

    with open("userdata.json", "r") as f:
        userdata = json.load(f)
    
    if omit is not None:
        services_map = {k: v for k, v in services_map.items() if k not in omit}

    for service in services_map:
        submap = services_map[service]
        broker_email = submap["privacy_dept_contact_email"]
        sender = userdata["email"]
        if isinstance(sender, list):
            sender = sender[0] # send from first listed email address
        
        # Generate message content
        text = generate_plain_text(userdata, submap, template="template.txt")
        html = generate_html(userdata, submap, template="template.html")

        # Create an EmailMessage object
        msg = EmailMessage()
        msg["Subject"] = "Data deletion request"
        msg["From"] = sender
        msg["To"] = broker_email

        # Set the plain text and HTML content
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()
            try:
                server.login(username, password)
            except smtplib.SMTPServerDisconnected:
                print("Connection closed unexpectedly. Retrying in 5 minutes...")
                print("Omit from next run:", omit)
                time.sleep(300)
                send_emails(services_map, username, password, 
                            userdata="userdata.json", omit=omit)

            try:
                server.send_message(msg)
                print("Email sent to:", service)
                omit.append(service)

            except Exception as error_message:
                print("Email failed to send to:", service)
                unsuccessful[service] = [broker_email, error_message]
    
    with open("sent_emails.json", "w") as f:
        json.dump(successful, f)
    with open("unsent_emails.json", "w") as f:
        json.dump(unsuccessful, f)

def get_login_credentials() -> (str, str):
    username = input("Username: ")
    password = getpass("Password: ")

    with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
        server.starttls()
        try:
            server.login(username, password)
        except Exception as error_message:
            print("Failed to login to mail server.", error_message)
    
    return username, password

if __name__ == "__main__":
    username, password = get_login_credentials()
    services = csv_to_map(service_list="services_list_06May2021.csv", 
                          subset="all")
    omit = []
    send_emails(services, username, password, userdata="userdata.json",
                omit=omit)
   