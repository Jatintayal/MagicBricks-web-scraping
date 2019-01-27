
# Import some modules which we'll be using in this project.

from bs4 import BeautifulSoup                             #Beautiful Soup is a Python package for parsing HTML and XML documents.
from selenium import webdriver							  #WebDriver is a web automation framework that allows you to execute your tests against different browsers.
import requests                                           #Requests is a Python HTTP library.
import time                                               #time has a sleep() function which can be used to pause the execution.
import re                                                 #re is used in raw string manipulation.
import numpy as np, pandas as pd                          #Numpy is used to convert a list into a numpy array then I used Pandas to convert it into a DataFrame and then save it as .csv file.


def get_the_details(link):                                #This function crawls the individual web pages for the information of specified variables.
    
    bedrooms = 0                                          #On sites like MagicBricks there may be some missing data which can cause errors during the execution so I'm initializing these variables here.
    bathrooms = 0
    balcony = 0
    super_area = 0
    price_per_sqft = ''
    status = ''
    transaction_type = ''
    floor = ''
    car_parking = 'None'
    furnished_status = ''
    lift = 'No'
    landmarks = ''
    aoc = ''
    pc = ''
    rent = ''
    EMI = ''
    
    req = requests.get(link)                             #Making a request.
    bs = BeautifulSoup(req.text, 'html.parser')          #Parsing the web page.
    
	#In the following code I used functions like strip() and replace() to get the structured data out of the text.
    headline = bs.find('div', {'class':'propBhk'}).find('span', {'class':'p_bhk'}).text.strip()                         
    price = bs.find('div', {'class':'p_price'}).text.strip()[2:]
    address1 = bs.find('div', {'class':'propBhk'}).find('span', {'class':'p_text'}).text.strip()[12:].replace('\n', '').strip()
    
	#row1, row2, row 3 are three rows in 'p_infoColumn' which contains most of the data on the property.
    row1 = re.sub(' +', ' ', bs.find_all('div', {'class':'p_infoRow'})[0].text.replace('\n', ' ').strip()).split(' ')
	
    for i in range(len(row1)):
	
        if row1[i] == 'Bedrooms' or row1[i] == 'Bedroom':
            bedrooms = row1[i + 1]
			
        if row1[i] == 'Bathrooms'or row1[i] == 'Bathroom':
            bathrooms = row1[i + 1]
			
        if row1[i] == 'Balconies'or row1[i] == 'Balcony':
            balcony = row1[i + 1]
			
    
    row2 = re.sub(' +', ' ', bs.find_all('div', {'class':'p_infoRow'})[1].text.replace('\n', ' ').strip()).split(' ')
	
    if 'Super' in row2:
        super_area = row2[2]
		
    elif 'area' in row1:
        super_area = row1[2]
		
    if 'Sq-ft' in row2:
        price_per_sqft = row2[-1].split('/')[0]
    
	
    row3 = re.sub(' +', ' ', bs.find_all('div', {'class':'p_infoRow'})[3].text.replace('\n', ' ').strip()).split(' ')
    
    if row3[1] == 'Ready':
        status = 'Ready to Move'
		
    elif row3[1] == 'Under':
        status = 'Under Construction'
		
    for i in range(len(row3)):
		
        if row3[i] == 'type':
            transaction_type = row3[i + 1]
			
        elif row3[i] == 'Floor':
			
            if len(row3[i + 1]) == 7:                                                                             #I am seperating ones and tens digits because some characters were appearing between the digit and (.
				floor = row3[i + 1][:2] + ' (Out of ' + row3[i + 3] + ' floors)'  
				
            elif len(row3[i + 1]) == 6:
                floor = row3[i + 1][:1] + ' (Out of ' + row3[i + 3] + ' floors)'
				
        elif row3[i] == 'parking' and row3[i + 1] != 'None':
            car_parking = row3[i + 1] + ' ' + row3[i + 2]
			
            if (i + 4) < len(row3):
			
                if row3[i + 4] == 'Open':
                    car_parking = car_parking + ' ' + row3[i + 3] + ' Open'
					
        elif row3[i] == 'status':
            furnished_status = row3[i + 1]
    
	#Lift variable is present on different places for different properties so I initialized the variable with a 'No' and if it finds the Lift in amenities then it will turn to 'Yes' but if it finds lift in description section then it will turn to 'yes, (the number of lifts)'.
    amenities = bs.find('div', {'class':'amenListIcons'})
	
    if amenities:
	
        for i in amenities.find_all('span', {'class':'amenValT'}):
		
            if i.text == 'Lift':
                lift = 'Yes'
				
    if lift == 'No':
        desc = bs.find('div', {'class':'descriptionCont'}).find_all('div', {'class':'p_infoRow'})
		
        for i in desc:
		
            if 'Lift' in i.text:
                lift = 'Yes, ' + i.text.replace('\n', '')[-1]
                break
    
	
    column = bs.find('div', {'class':'descriptionCont'}).find_all('div', {'class':'p_infoRow'})
    
    for i in range(len(column)):
        column[i] = column[i].text.replace('\n', ' ').strip()
		
        if 'Price Breakup' in column[i]:
            price_breakup = column[i][20:].split(' ')[0] + ' ' + column[i][20:].split(' ')[1]
			
        elif 'Address' in column[i]:
            address2 = column[i][8:-14]
			
        elif 'Landmarks' in column[i]:
            landmarks = column[i][10:]
			
        elif 'Age of Construction' in column[i]:
            aoc = column[i][20:]
			
    description = column[0]
	
    if description[-1] is 'e':                                     #Some description texts had a 'more' word at the end so I removed them here.
		description = description[:-4].strip()
    
	
    quick_facts = re.sub(' +', ' ', bs.find('div', {'class':'quick_row'}).text.replace('\n', ' ')).split(' ')
	
    for i in range(len(quick_facts)):
	
        if quick_facts[i] == 'comparison':
            pc = quick_facts[i + 1] + ' ' + quick_facts[i + 2] + ' than the avg. price'
			
        elif quick_facts[i] == 'rent':
            rent = '₹ ' + quick_facts[i + 2] + ' per month'
			
        elif quick_facts[i] == 'EMI':
		
            for j in range(i + 1, len(quick_facts) - 1):
			
                if quick_facts[j] == '₹':
                    continue
					
                EMI = EMI + quick_facts[j] + ' '
	
	
    agent = bs.find('div', {'class':'nameValue'})
	
    if not agent:
        agent = bs.find('div', {'class':'CAName'}).text.replace('\n', '')
		
    else:
        agent = agent.text.strip()
		
		
	#Now that we have all of our variables ready, we can return them as a list.
    lst = [headline, price, address1, bedrooms, bathrooms, balcony, super_area, price_per_sqft, status, transaction_type, floor, car_parking, furnished_status, lift, description, price_breakup, address2, landmarks, aoc, pc, rent, EMI, agent]
    
	return(lst)                #Returning the list.
	
	
	
def get_the_properties():                                       #The main crawler which crawls the 'infinite scroll' page to get the individual property links from the blocks and the returns the details of all the properties on that web page.

    driver = webdriver.Firefox()                                #WebDriver is a remote control interface that enables introspection and control of Firefox() as driver.
	
    driver.get('https://www.magicbricks.com/property-for-sale/residential-real-estate?proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa,Residential-Plot&cityName=Bangalore')                   #The link to open in the remote controlled interface.
    
	lastHeight = driver.execute_script('return document.body.scrollHeight')                                     #Geting the current height of the web page.
	
    while True:                                                                                                 #Run the loop until the end of page comes.
	
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")                                #Scroll down to the current end of the page.
        time.sleep(10)                                                                                          #Pause the execution for 10 sec so that the page can load in that time.
        newHeight = driver.execute_script("return document.body.scrollHeight")                                  #Get the new height of the web page.
		
        if newHeight == lastHeight:                                                                             #Stop the loop if the end is here.
            break
			
        lastHeight = newHeight
		
    bs = BeautifulSoup(driver.page_source)                                                                      #Parsing the web page.
    blocks = bs.find_all("div", {'class':'m-srp-card__heading clearfix'})                                       #Get the individua property blocks.
    properties = []
	
    for i in blocks:                                                                                            #Loop through all the blocks to get the links.
        properties.append(get_the_details(i.find('a', {'class':'m-srp-card__title'}).get('href')))              #Call get_the_details() function with the link.
		
    return properties                                                                                           #Return the list of property details.
	
	
properties = get_the_properties()                                                                               #Call the get_the_properties() function to get the list of properties.

arr = np.array(properties)                                                                                      #Convert the list into a numpy array.
df = pd.DataFrame(arr, columns=['Headline', 'Price', 'Address', 'Bedrooms', 'Bathrooms', 'Balcony', 'Super Area', 'Price per sqft', 'Status', 'Transaction Type', 'Floor', 'Car parking', 'Furnished status', 'Lifts', 'Description', 'Price breakup', 'Address', 'Landmarks', 'Age of construction', 'Price comparison', 'Expected rent', 'Monthly EMI', 'Owner/Builder'])              #Convert the numpy array into a dataframe.

df.to_csv('magic_bricks.csv')                                                                                   #Save the DataFrame as a csv file.