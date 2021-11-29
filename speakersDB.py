from flask import Flask, render_template, flash, request, redirect, Blueprint, url_for
from flask_login import login_required, current_user
import os
import configparser
import requests
import json
# from werkzeug import secure_filename


from mysql_commands import mysql_fetchall, mysql_insert, mysql_update, mysql_delete
from EventsDB.event_functions import update_speaker_sql

# ** Blueprint stuff
main = Blueprint('speakersdb', __name__, template_folder='templates', static_folder='static', url_prefix='/speakersdb')


# Config settings
configFile = configparser.ConfigParser()
configFile.read('config.txt')


def find_speaker_hubspot(first, last):
    if len(first) > 1 and len(last) > 1:
        url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        querystring = {"hapikey": configFile.get('hubspot', 'apikey')}
        payload = '{"filters":[{"propertyName": "firstname","operator": "EQ", "value": "' + first + '"},{"propertyName": "lastname","operator": "EQ","value": "' + last + '"}],"properties":[ "email", "firstname","lastname","company", "company_type", "company_s_tech_sector", "gender", "linkedin_person_", "hubspot_owner_id", "company_s_uk_region","d_i_area_of_expertise", "d_i_area_of_interest", "notes_last_updated","jobtitle","twitterhandle","hubspot_owner_id"]}'
        headers = {
            'accept': "application/json",
            'content-type': "application/json"
        }
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        jsonObj = json.loads(response.text)
        results = jsonObj['results']
        # print(results)
        return results
    else:
        flash("Please make sure you add first and last name")



def speakers_info(speakerFN, speakerLN):
    searched_speaker = []
    if speakerFN or speakerLN:
        if len(speakerFN) > 1 and len(speakerLN) > 1:
            # print(find_speaker_hubspot(speakerFN, speakerLN))
            for p in find_speaker_hubspot(speakerFN, speakerLN):
                fullNameList = []
                fullNameList.append(p['properties']['firstname'] + " " + p['properties']['lastname'])
                fullNameList.append(str(p['properties']['company']))
                fullNameList.append(p['id'])
                # print(fullNameList)
                searched_speaker.append(fullNameList)
    return render_template('new_speaker_template.html', speakers = searched_speaker, fn = speakerFN, ln = speakerLN, speaker_details = find_speaker_hubspot(speakerFN, speakerLN))


# def upload_pic():
#     uploadedFile = request.files['picture']
#     if uploadedFile.filename != "":
#         fileName = secure_filename(uploadedFile.filename)
#         uploadedFile.save(os.path.join('speakersdb/uploads/', fileName))
#         return print("done")
#     else:
#         pass



@main.route('/')
@login_required
def speakers_list():
    # speakers = "SELECT p.email, p.first_name,p.last_name, p.job_title_hubspot, p.gender_hubspot, p.contact_owner_hubspot, t.rating, p.last_contacted_hubspot, f.areas, f.interestedIn, t.notes, t.DnI_expertise, t.DnI_interests, t.id, p.ID, t.companyid FROM customer_data.speakers AS t RIGHT JOIN customer_data.speakers_form AS f ON t.person_id = f.person_id INNER JOIN customer_data.person AS p ON t.person_id = p.id order by p.last_contacted_hubspot DESC"
    speakers = "SELECT p.email, p.first_name,p.last_name, p.job_title_hubspot, p.gender_hubspot, p.contact_owner_hubspot, t.rating, p.last_contacted_hubspot, t.notes, t.DnI_expertise, t.DnI_interests, t.id,p.ID, t.companyid, f.areas, f.interestedIn, f.id FROM customer_data.person AS p INNER JOIN customer_data.speakers AS t ON  p.id = t.person_id LEFT JOIN customer_data.speakers_form AS f ON t.person_id = f.person_id order by p.last_contacted_hubspot DESC"
    all_speakers = mysql_fetchall(speakers)
    # print(all_speakers)
    speakers_consent = "SELECT p.email, f.person_id, p.ID, f.diversity_consent FROM customer_data.person AS p LEFT JOIN customer_data.speakers_form AS f ON p.id = f.person_id"
    all_speakers_consent = mysql_fetchall(speakers_consent)
    # print(all_speakers_consent)
    # events = "SELECT t.id, t.person_id, e.event_name, pe.speaker_status FROM customer_data.speakers AS t RIGHT JOIN customer_data.people_events AS pe ON t.person_id = pe.person_id LEFT JOIN customer_data.events AS e ON pe.event_id = e.id"
    events ="SELECT t.id, t.person_id, e.event_name, pe.speaker_status FROM customer_data.speakers AS t INNER JOIN customer_data.people_events AS pe ON t.person_id = pe.person_id LEFT JOIN customer_data.events AS e ON pe.event_id = e.id WHERE pe.speaker_status != 'removed'"
    previous_events = mysql_fetchall(events)
    # print(previous_events)
    company = "SELECT o.name, o.company_type, o.tech_sector, t.id, o.id FROM customer_data.speakers AS t INNER JOIN customer_data.org AS o ON t.companyid = o.id"
    org_info = mysql_fetchall(company)
    # print(org_info)
    return render_template('speakerlistview.html', speakers=all_speakers, events=previous_events, org=org_info, speaker_form=all_speakers_consent)


@main.route('/profile')
@login_required
def spekaersProfile():
    personID = (str(request.args.get('id')),)
    speaker_info = "SELECT p.email, p.first_name,p.last_name, p.job_title_hubspot,p.linkedin_hubspot,p.twitter_hubspot,p.contact_owner_hubspot,p.gender_hubspot, p.last_contacted_hubspot,p.source_hubspot,t.rating, p.last_contacted_hubspot, t.notes, t.DnI_expertise, t.DnI_interests, t.bio, t.id,p.ID, t.companyid,f.id,f.areas, f.other_areas,f.interestedIn, f.diversity_consent,f.submitted_date, dni.yob, dni.pronoun, dni.pronoun_other, dni. identify, dni. identify_other, dni.sexuality, dni.sexuality_other, dni.country_origin, dni.nationality, dni.ethnicity, dni.ethnicity_other, dni.disability, dni.neurodivergent, dni.religion, dni.religion_other, dni.school_type, dni.school_type_other, dni.parent_qualification, dni.parent_qualification_other, dni.date_submitted FROM customer_data.person AS p INNER JOIN customer_data.speakers AS t ON  p.id = t.person_id LEFT JOIN customer_data.speakers_form AS f ON t.person_id = f.person_id  Left JOIN customer_data.speakersD_n_I AS dni ON t.person_id = dni.person_id WHERE p.id = %s"
    speakerInfo = mysql_fetchall(speaker_info, personID)
    # print(speakerInfo[0][16])
    speakerID = speakerInfo[0][16]
    speaker_company = "SELECT s.person_id, c.name, c.city, c.uk_region, c.website, c.company_type, c.tech_sector FROM customer_data.speakers as s INNER JOIN customer_data.org as c ON s.companyid = c.ID WHERE s.id = %s"
    companyInfo = mysql_fetchall(speaker_company, (speakerID, ))
    # print(companyInfo)
    events = "SELECT pe.attended, pe.speaker_status, e.event_name, e.programme FROM customer_data.people_events as pe INNER JOIN customer_data.events as e ON pe.event_id=e.id WHERE pe.person_id= %s"
    events_participating = mysql_fetchall(events, personID)
    # print(events_participating)
    return render_template('profile.html', speaker_details=speakerInfo[0], speaker_company_info=companyInfo, events=events_participating)



@main.route('/add')
@login_required
def newSpeaker():
    return render_template('new_speaker_template.html')


@main.route('/submit', methods=['POST'])
@login_required
def signup():
    if request.form.get("search") == 'Search':
        speakerFN = request.form['speakerFN']
        speakerLN = request.form['speakerLN']
        return speakers_info(speakerFN, speakerLN)
    elif request.form.get("add") == 'Add':
        brandNewSpeaker = request.form['newSpeaker2']
        fname_update = request.form['fname']
        # print(fname_update)
        lname_update = request.form['lname']
        email_update = request.form['email']
        # print(email_update)
        job_title_update = request.form['job_title']
        twitter_update = request.form['twitter']
        linkedin_update = request.form['linkedin']
        gender_update = request.form['gender']
        contact_owner_update = request.form['contact_owner']
        last_engaged_update = request.form['last_engaged']
        # print(last_engaged_update)
        rating_update = request.form['rating']
        bio_update = request.form['bio']
        # picture_upload = upload_pic()
        search_person = "SELECT ID FROM person where email = %s"
        email = (email_update, )
        myresult = mysql_fetchall(search_person, email)
        # print(myresult)
        if myresult and not brandNewSpeaker:
            update_person = "UPDATE person set email=%s, first_name=%s, last_name=%s, job_title_hubspot=%s, linkedin_hubspot=%s, twitter_hubspot=%s, contact_owner_hubspot=%s, gender_hubspot=%s, last_contacted_hubspot=%s where ID=%s"
            eventDetails = (email_update, fname_update, lname_update,job_title_update, linkedin_update, twitter_update, contact_owner_update, gender_update, last_engaged_update, myresult[0][0])
            mysql_update(update_person, eventDetails)
            search_speaker = "SELECT ID FROM speakers where person_id = %s"
            person_id = myresult[0]
            myspeaker = mysql_fetchall(search_speaker, person_id)
            if myspeaker:
                update_speaker = "UPDATE speakers set person_id=%s, rating=%s, bio=%s, last_reviewed=%s where id=%s"
                speakerDetails = (person_id[0], rating_update, bio_update, last_engaged_update, myspeaker[0][0])
                mysql_update(update_speaker, speakerDetails)
            else:
                newSpeaker = "INSERT INTO speakers (person_id, rating, bio, last_reviewed) VALUES (%s,%s,%s,%s)"
                speakerDetails = (person_id[0], rating_update, bio_update, last_engaged_update)
                mysql_insert(newSpeaker, speakerDetails)
        elif not myresult:
            newPerson = "INSERT INTO person (email, first_name, last_name, job_title_hubspot, linkedin_hubspot, twitter_hubspot, contact_owner_hubspot, gender_hubspot, last_contacted_hubspot) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            personDetails = (email_update, fname_update, lname_update, job_title_update, linkedin_update, twitter_update, contact_owner_update, gender_update, last_engaged_update)
            mysql_insert(newPerson, personDetails)
            insertID = "INSERT INTO speakers (person_id) SELECT ID FROM person WHERE email = %s"
            email_updates = (email_update, )
            mysql_insert(insertID, email_updates)
            newSpeaker = "UPDATE speakers as s SET s.rating=%s, s.bio=%s, s.last_reviewed=%s where s.person_id = (SELECT p.ID FROM person as p WHERE p.email = %s)"
            updates = (email_update)
            speakerDetails = (rating_update, bio_update, last_engaged_update, updates)
            mysql_update(newSpeaker, speakerDetails)
    elif request.form.get("update") == 'Update':
        update = request.form.to_dict(flat=False)
        person_id = request.form.getlist('id')
        for x, y in update.items():
            # print(x, y[0])
            update_speaker_sql(x,y[0],person_id[0])

    return redirect(url_for('speakersdb.speakers_list'))
