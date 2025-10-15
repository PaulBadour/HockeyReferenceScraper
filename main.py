from selenium import webdriver
from selenium.webdriver.common.by import By

def getPlayerPage(name: str, offset: int = 1):
    spacedName = name.lower().split(" ")
    firstName, lastName = spacedName[0], " ".join(spacedName[1:])

    shortLastName = lastName.replace(" ", "")[:5] if len(lastName.replace(" ", "")) >= 5 else lastName.replace(" ", "")
    URLEnd = f"{lastName[0]}/{shortLastName}{firstName[:2]}0{offset}.html"

    URL = f"https://www.hockey-reference.com/players/{URLEnd}"
    print(URL)
    driver = webdriver.Chrome()
    driver.get(URL)

    return driver

getPlayerPage("Lucas Raymond")