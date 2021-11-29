import requests
import mysql.connector
import json
import configparser

parser = configparser.ConfigParser()
parser.read('config.txt')
host = parser.get('localdb','host')
user = parser.get('localdb','user')
passwd = parser.get('localdb','passwd')
database = parser.get('localdb','database')

mydb = mysql.connector.connect(
    host=host,
    user=user,
    passwd=passwd,
    database=database
)
mycursor = mydb.cursor()

# calls all records imported with the event form
missingID = "SELECT ID, email, hubspot_id, hubspot_associated_company_id, job_title_hubspot, linkedin_hubspot, twitter_hubspot, contact_owner_hubspot, gender_hubspot, last_contacted_hubspot, source_hubspot FROM person WHERE hubspot_id is null AND mobilize_id is null AND email !=''"
mycursor.execute(missingID)
all_missingID = mycursor.fetchall()
# print(all_missingID)
# DnI_interests, DnI_expertise from speaker

# calls hubspot api to look for the id
url = "https://api.hubapi.com/crm/v3/objects/contacts/search"

querystring = {"hapikey":parser.get('hubspot','apikey')}
for element in all_missingID:
    # print(element)
    ids = element[0]
    email = element[1]
    payload = '{"filterGroups":[{"filters":[{"propertyName": "email","operator": "EQ","value": "' + email + '"}]}]}'
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
        }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    print(response.text)
    jsonObj = json.loads(response.text)
    # print("jsonObj type=", type(jsonObj))
    # if not jsonObj['results']:
    #     pass
    # else:
    #     results = jsonObj['results']
    #     # print(results)
    #     hubspot_id = results[0]['id']
    #
    #     add_id = "UPDATE person set hubspot_id=%s where ID=%s"
    #     person_details = (hubspot_id, ids)
    #     mycursor.execute(add_id, person_details)
    #     mydb.commit()
    #
    #     url2 = "https://api.hubapi.com/crm/v3/objects/contacts/" + hubspot_id + "/associations/company"
    #     querystring2 = {"limit": "500", "hapikey": parser.get('hubspot', 'apikey')}
    #     headers2 = {'accept': 'application/json'}
    #     response2 = requests.request("GET", url2, headers=headers2, params=querystring2)
    #     # print(response2.text)
    #     jsonObj2 = json.loads(response2.text)
    #     results2 = jsonObj2['results']
    #
    #     if not results2:
    #         pass
    #     else:
    #         company_id = results2[0]['id']
    #         add_id = "UPDATE person set hubspot_associated_company_id=%s where ID=%s"
    #         person_details = (company_id, ids)
    #         mycursor.execute(add_id, person_details)
    #         mydb.commit()

print("done")
