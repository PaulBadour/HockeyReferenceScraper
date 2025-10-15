from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import os

def getScorecard(team:str, date: str = None):
    dtformat = "%Y-%m-%d"
    
    
    if not date:
        today = datetime.now()
        schedYear = today.year if today.month >= 9 else today.year + 1
        schedDriver = webdriver.Chrome()
        schedDriver.get(f"https://www.nhl.com/redwings/schedule/{schedYear}/fullseason")
        

        try:
            WebDriverWait(schedDriver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='sc-ivtqZH lfNkHP']"))
            )
        except TimeoutException:
            print("Schedule Timed Out")
            schedDriver.close()
            return

        dates = schedDriver.find_elements(By.XPATH, "//div[@class='sc-bfEblg hHBrXt']/h3")
        prevDate = None
        for i in dates:
            dt = datetime.strptime(i.get_attribute("innerHTML"), "%A, %B %d")
            if dt.month < 9:
                dt = dt.replace(year=schedYear + 1)
            else:
                dt = dt.replace(year=schedYear)
            if (today - dt).days <= 0:
                date = prevDate.strftime(dtformat)
                break

            prevDate = dt
        if not date:
            print("Game not found")
            schedDriver.close()
            return
        schedDriver.close()
    

    driver = webdriver.Chrome()
    driver.get("https://www.hockeystatcards.com/impact")

    dateSelector = None
    try:
        dateSelector = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
    except TimeoutException:
        print("Timed Out")
        driver.close()
        return
    
    currDate = datetime.strptime(dateSelector.get_attribute("value"), dtformat)
    targetDate = datetime.strptime(date, dtformat)

    timeDelta = currDate - targetDate

    if timeDelta.days > 0:
        yearButton = None
        monthButton = None

        dateSelector.click()

        while timeDelta.days >= 365 or (timeDelta.days > 334 and currDate.month == targetDate.month):
            if not yearButton:
                yearButton = driver.find_element(By.XPATH, "//button[@aria-label='Go back 12 months']")
            yearButton.click()

            leapYear = True if currDate.year % 4 == 0 and (currDate.year % 100 != 0 or currDate.year % 400 == 0) else False
            dayChange = 366 if leapYear else 365
            currDate -= timedelta(days=dayChange)
            timeDelta = currDate - targetDate

        currMonth = currDate.month
        while currMonth != targetDate.month:
            if not monthButton:
                monthButton = driver.find_element(By.XPATH, "//button[@aria-label='Go back 1 month']")
            monthButton.click()
            currMonth = currMonth - 1 if currMonth > 1 else 12
    
        buttonLabel = targetDate.strftime("%a %b %d %Y")
        dayButton = driver.find_element(By.XPATH, f"//button[@aria-label='{buttonLabel}']")
        dayButton.click()
    
    gameSelector = None
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "homeImpact"))
        )
    except TimeoutException:
        print("Timed Out")
        driver.close()
        return

    gameSelector = driver.find_element(By.XPATH, "//div[@class='chakra-select__wrapper css-42b2qy']/select")
    options = gameSelector.find_elements(By.TAG_NAME, "option")
    found = False
    homeTeam = True


    for i in options:
        if team in i.get_attribute("innerHTML"):
            i.click()
            found = True

            if i.get_attribute("innerHTML").split()[0] == team:
                homeTeam = False

            break

    if not found:
        print("Game Card not found")
        driver.close()
        return

    id = "homeImpact" if homeTeam else "visImpact"

    
    try:
        card = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, id))
        )
    except TimeoutException:
        print("Timed Out")
        driver.close()
        return

    if not homeTeam:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    if not card.screenshot(f'{os.getcwd()}\screenshots\\{team}_{date}.png'):
        print("Screenshot error")

    driver.close()
    return

getScorecard("Panthers", "2025-10-07")