from bs4 import BeautifulSoup
import requests
import json
import smtplib

DATABASE_PATH = "file.txt" # Specify a specific path if you want the database to be located somewhere else. If not it will be in the root folder.
GMAIL_USERNAME = ""
GMAIL_PASSWORD = ""
GMAIL_RECIPIENTS = [""] # Can be multiple recipients separated by a comma

try:
    apartments = eval(open(DATABASE_PATH, 'r').read())
except:
    with open(DATABASE_PATH, 'w') as file:
        file.write("{}")
    apartments = eval(open(DATABASE_PATH, 'r').read())

def sendEmail(TEXT):
    # Standard code for sending an email.
    gmail_user = GMAIL_USERNAME
    gmail_pwd = GMAIL_PASSWORD
    TO = GMAIL_RECIPIENTS
    SUBJECT = "Apartment Listing Changes!"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    BODY = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    server.sendmail(gmail_user, TO, BODY)


def scrapeApartments():
    headers = {'User-Agent': 'Mozilla/5.0'}

    page = requests.get(
        "https://chicagorentals.com/apartment/the-flamingo/", headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all('section', id="available-apartments")
    apartmentUnits = []
    apartmentPrices = []
    apartmentInfo = []

    # Loads relevant information into lists for analysis
    for result in results:
        unit = result.find_all("h3")
        for uni in unit:
            if uni.text != "Available Apartments":
                apartmentUnits.append(uni.text)
        price = result.find_all("div", class_="unit-price")
        for pri in price:
            apartmentPrices.append(pri.text)
        info = result.find_all("div", class_="unit-data")
        for inf in info:
            test = " ".join(inf.text.split())
            apartmentInfo.append(test)

        TEXT = ""
        for unit, price, info in zip(apartmentUnits, apartmentPrices, apartmentInfo):
            # Checks if the apartment listing exists in our database.
            # Adds if it doesnt and will add the information to the email text.
            if unit not in apartments:
                print("Adding", unit)
                data = "[+]", unit, price, info, "\n"
                TEXT += " ".join(data)
                apartments[unit] = [price, info]
            # If it already exists in our database, it will double check to ensure the price is correct.
            # Updates the price if it has changed.
            elif price != apartments[unit][0]:
                print("Updating price")
                data = "[$]", unit, "price change --", apartments[unit][0], "to", price, "\n"
                TEXT += " ".join(data)
                apartments[unit][0] = price

        removal = []
        # Will remove the units that no longer appear on the website from our database.
        # Adds the removed unit to the email.
        for unit in apartments:
            if unit not in apartmentUnits:
                print("Removing", unit)
                data = "[-]", unit, apartments[unit][0], apartments[unit][1], "\n"
                removal.append(unit)
                TEXT += " ".join(data)
        for remove in removal:
            apartments.pop(remove)
            
        # Will send an email if anything was appended to the email body.
        if TEXT:
            sendEmail(TEXT)
            print('Email sent')
            with open(DATABASE_PATH, 'w') as file:
                file.write(json.dumps(apartments))
        else:
            print("No new changes")


if __name__ == "__main__":
    scrapeApartments()