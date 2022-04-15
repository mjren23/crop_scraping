# ### Things to think about
# - Error handling
# - Running script unsupervised
# - Pausing in between scrapes
import time
import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
from dotenv import load_dotenv
import os
from interface_trackers import get_finished_set, get_last_done, mark_done
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from dropbox.exceptions import AuthError
import datetime
import sys


# TODO: documentation


# returns list of states, districts, etc in tuple formatted like ("NAME", "3b")
def parse_list(list_places):
    split = list_places.split("|")
    to_return = []
    for string in split:
        extracted = re.search(",(.*)", string).group(1).strip()
        num = re.search("^(.*?),", string).group(1)
        if "&amp;" in extracted:
            extracted = extracted.replace("&amp;", "&")
        to_return.append((extracted, num))
    return to_return


def save_file(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    no_record = soup.find("div", text="No Record Found")
    if no_record is not None:  # no record available
        return -1

    initial = soup.find("div", text="Sl No")

    headers = []
    for col in initial.parent.parent:
        headers.append(col.get_text())

    headers = headers[1:]
    data = []
    row_number = 0
    curr_row = initial.parent.parent

    while row_number < 18:
        row_data = []
        curr_row = curr_row.next_sibling
        for col in curr_row:
            row_data.append(col.get_text())
        row_data = row_data[1:]
        data.append(row_data)
        row_number += 1

    df = pd.DataFrame(data=data, columns=headers)
    file_name = gen_file_name() + ".csv"
    df.to_csv(local_path_tables + file_name)
    return file_name


def upload_file(local_file_name):
    with open(local_file_name, 'rb') as f:
        try:
            dbx.files_upload(f.read(), "/" + local_file_name, mode=WriteMode.overwrite)
            if VERBOSE_LOGGING:
                log("successfully uploaded file " + local_file_name + " to dropbox")
            return 0
        except (ApiError, AuthError):
            dbx.refresh_access_token()
            if VERBOSE_LOGGING:
                log("unable to upload file " + local_file_name + " to dropbox")
            return -1



def check_already_done(check_year, check_state, check_district, check_tehsil, check_crop):
    if (str(check_year), check_state.replace(" ", ""), check_district.replace(" ", ""), check_tehsil.replace(" ", ""), check_crop.replace(" ", "")) in finished:
        return True
    return False


# note: if tehsil has forward slash "/" in it, will replace with "-"
def gen_file_name():
    return str(year) + "_" + state[0].replace(" ", "") + "_" + district[0].replace("/", "-").replace(" ", "") + "_" + tehsil[0].replace(
        " ", "").replace("/", "-") + "_" + crop[
               0].replace(" ", "")


# saves message along with current time when log is called
def log(message):
    global curr_log_file
    if curr_log_file == "":
        new_path = os.path.relpath('logs/' + "log_number.txt", os.path.dirname(__file__))
        with open(new_path, "r+") as log_num:
            curr_num = int(log_num.read())
            log_num.seek(0)
            curr_log_file = "log_file_" + str(curr_num) + ".txt"
            log_num.write(str(curr_num + 1))
            log_num.truncate()
    new_path = os.path.relpath('logs/' + curr_log_file, os.path.dirname(__file__))
    with open(new_path, "a+") as log_file:
        message = message + ", " + str(datetime.datetime.now())
        log_file.write(message)
        log_file.write("\n")


def try_request(request_obj, is_home_request=False, is_eventval_request=False, is_table_request=False):
    new_wait_time = WAIT_TIME
    if VERBOSE_LOGGING:
        log("sending request to " + request_obj.url)
    while True:
        try:
            response = session.send(request_obj, timeout=REQUESTS_TIMEOUT)
            if response.status_code == 200 and not (is_home_request or is_eventval_request or is_table_request):
                return response
            elif response.status_code == 200:
                if is_home_request:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    if len(soup.select("#__VIEWSTATE")) > 0:
                        return response
                elif is_eventval_request:
                    soup = BeautifulSoup(response.text, "html.parser")
                    if len(soup.select("#__EVENTVALIDATION")) > 0:
                        return response
                elif is_table_request:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    if soup.find("div", text="Sl No") is not None or soup.find("div",
                                                                               text="No Record Found") is not None:
                        return response
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as error:
            log(str(error) + " while handling request to " + request_obj.url)

        if new_wait_time > GIVE_UP:
            log("website still hanging after waiting " + str(GIVE_UP) + " seconds, exiting.")
            exit_program()
        if VERBOSE_LOGGING:
            log("waiting " + str(new_wait_time) + " seconds... for request to " + request_obj.url)
        time.sleep(new_wait_time)
        new_wait_time = new_wait_time * BACKOFF


def record_file(state_name, file_name_or_message, upload_problem):
    tracker_file = "state_trackers/" + state_name.replace(" ", "") + (
        "_dropbox_problem.txt" if upload_problem else "_unsuccessful.txt")
    with open(tracker_file, "a+") as record:
        record.write(file_name_or_message)
        record.write("\n")


def except_hook(exctype, value, traceback):
    log(str(exctype) + str(traceback) + str(value))
    exit_program()


# finish uploading log files
def exit_program(exctype=None, value=None, traceback=None):
    # upload most recent log file
    upload_file("logs/" + curr_log_file)
    # upload most recent state tracker
    to_upload = last_done["state"].replace(" ", "") + "_unsuccessful.txt"
    upload_file("state_trackers/" + to_upload)
    if exctype is not None:
        sys.__excepthook__(exctype, value, traceback)
    sys.exit(-1)



years = [2000, 2015, 2005, 2010]
years_text = ["2000-01", "2015-16", "2005-06", "2010-11"]
crops = [("PADDY", "101"), ("WHEAT", "106"), ("MAIZE", "104"), ("SOYABEAN", "1009"), ("COTTON", "1101"),
         ("GROUNDNUT", "1001"),
         ("RAPESEED & MUSTARD", "1004"), ("BAJRA", "103"), ("SUGARCANE", "401"), ("JOWAR", "102")]
session = requests.Session()
load_dotenv()
USER = os.getenv("DROPBOX_KEY")
PASS = os.getenv("DROPBOX_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")


headers_json = {'Content-Type': "application/json; charset=utf-8"}
headers_url = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate, br",
               "Content-Type": "application/x-www-form-urlencoded",
               "Connection": "keep-alive",
               }

curr_log_file = ""

local_path_tables = "saved_tables/"
finished = get_finished_set()
last_done = get_last_done()
sys.excepthook = except_hook

dbx = dropbox.Dropbox(oauth2_access_token=ACCESS_TOKEN, app_key=USER, app_secret=PASS, oauth2_refresh_token=REFRESH_TOKEN)
dbx.refresh_access_token()

BACKOFF = 2
WAIT_TIME = 1
GIVE_UP = 3600
REQUESTS_TIMEOUT = 30
CRAWLER_DELAY = 2


VERBOSE_LOGGING = False

log("BEGINNING OF LOG FILE")

for i in range(len(years)):
    year = years[i]
    year_text = years_text[i]

    if last_done != -1 and years.index(int(last_done["year"])) > i:
        continue

    home = requests.Request('GET', "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx")
    prepped_home = home.prepare()
    response_home = try_request(prepped_home, is_home_request=True)

    # # get home page
    # req_home = session.get("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx")
    #
    # parse w BS4
    home_html = response_home.text
    home_soup = BeautifulSoup(home_html, 'html.parser')

    # parse viewstate
    view_state = home_soup.select("#__VIEWSTATE")[0]['value']
    view_state_gen = home_soup.select("#__VIEWSTATEGENERATOR")[0]['value']
    log("got view state from home page")

    #
    # if view_state_gen is None or view_state is None:
    #     print("unable to parse viewstate")
    #     exit()

    # get states available for this year
    data_ddl = json.dumps({'value': str(year), 'Text': year_text, 'CallFor': 'Year'})

    # req_get_ddl = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/Get_ddlData",
    #                            headers=headers_json,
    #                            data=data_ddl)

    req_get_ddl = requests.Request('POST', "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/Get_ddlData",
                                   headers=headers_json,
                                   data=data_ddl)
    prepped_ddl = req_get_ddl.prepare()
    response_get_ddl = try_request(prepped_ddl)

    json_response_ddl = response_get_ddl.json()
    states_for_year = json_response_ddl['d']['State']
    states = parse_list(states_for_year)

    for state in states:
        if last_done != -1 and last_done["state"] > state[0]:
            continue
        # get districts for this state
        log("handling state " + str(state))
        data_district = json.dumps({'value': state[1], 'Text': state[0], 'CallFor': 'State', 'year': str(year)})
        # req_get_district = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getDistrict",
        #                                 headers=headers_json,
        #                                 data=data_district)
        req_get_district = requests.Request('POST',
                                            "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getDistrict",
                                            headers=headers_json,
                                            data=data_district)
        prepped_district = req_get_district.prepare()
        response_get_district = try_request(prepped_district)

        json_response_district = response_get_district.json()
        districts_for_state = json_response_district['d']['District']
        if "NOT AVAILABLE" in districts_for_state:
            log("found state for which survey was not conducted " + str(state) + ", " + str(year))
            record_file(state[0], "no data for this state recorded for year " + str(year), False)
            continue
        districts = parse_list(districts_for_state)
        for district in districts:
            if last_done != -1 and last_done["district"] > district[0] and last_done["state"] >= state[0]:
                continue
            # get tehsils for this district
            log("handling district " + str(district[0]))
            data_tehsil = json.dumps(
                {'value': district[1], 'Text': district[0], 'CallFor': 'District', 'stcdu': state[1],
                 'year': str(year)})
            # req_get_tehsil = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getTehsil",
            #                               headers=headers_json,
            #                               data=data_tehsil)

            get_tehsil = requests.Request('POST',
                                          "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getTehsil",
                                          headers=headers_json,
                                          data=data_tehsil)

            prepped_tehsil = get_tehsil.prepare()
            response_get_tehsil = try_request(prepped_tehsil)

            json_response_tehsil = response_get_tehsil.json()
            tehsils_for_district = json_response_tehsil['d']['Tehsil']
            # TODO: figure out why this if statement doesn't trigger
            if "NOT AVAILABLE" in tehsils_for_district or tehsils_for_district == "":
                log("found district for which survey was not conducted " + str(district[0]) + ", " + str(year))
                record_file(state[0], "no data for district " + district[0] + " recorded for year " + str(year), False)
                continue

            tehsils = parse_list(tehsils_for_district)

            for tehsil in tehsils:

                if last_done != -1 and last_done["tehsil"] > tehsil[0] and last_done["district"] >= district[0] and \
                        last_done["state"] >= state[0]:
                    continue

                log("handling tehsil " + tehsil[0])

                # check if cropping pattern is available
                data_crop = json.dumps(
                    {'year': year, 'State': state[1], 'Level': 'TehsilLevel', 'District': district[1],
                     'Tehsil': tehsil[1]})

                get_crop = requests.Request('POST',
                                            "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/Get_Crop",
                                            headers=headers_json,
                                            data=data_crop)
                prepped_crop = get_crop.prepare()
                response_get_crop = try_request(prepped_crop)

                # req_get_crop = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/Get_Crop",
                #                             headers=headers_json,
                #                             data=data_crop)

                text_response_crop = response_get_crop.json()['d']['Crops']

                for crop in crops:
                    if check_already_done(year, state[0], district[0], tehsil[0], crop[0]):
                        file_name_unsuccessful = gen_file_name()
                        log("file already scraped by genghe " + gen_file_name())
                        record_file(state[0], "Genghe already scraped " + file_name_unsuccessful, False)
                        continue

                    if crop[0] not in text_response_crop:
                        file_name_unsuccessful = gen_file_name()
                        record_file(state[0], file_name_unsuccessful, False)
                        continue

                    data_get_session = json.dumps({
                        "value1": [year_text, str(year), "CROPPING PATTERN", "6b", "ALL SOCIAL GROUPS", "4", crop[0],
                                   crop[1], state[0], state[1],
                                   district[0], district[1], tehsil[0], tehsil[1]]})

                    # req_get_session = session.post(
                    #     "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession",
                    #     headers=headers_json,
                    #     data=data_get_session)
                    # if req_get_session.status_code != 200:
                    #     continue

                    post_session = requests.Request('POST',
                                                    "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession",
                                                    headers=headers_json,
                                                    data=data_get_session)
                    prepped_session = post_session.prepare()
                    response_get_session = try_request(prepped_session)

                    # now make call to post_taluk
                    data_post_taluk = {'__VIEWSTATE': view_state,
                                       '__VIEWSTATEGENERATOR': view_state_gen,
                                       '__VIEWSTATEENCRYPTED': "",
                                       '_ctl0:ContentPlaceHolder1:ddlYear': str(year),
                                       '_ctl0:ContentPlaceHolder1:ddlState': state[1],
                                       '_ctl0:ContentPlaceHolder1:ddlDistrict': district[1],
                                       '_ctl0:ContentPlaceHolder1:ddlTehsil': tehsil[1],
                                       '_ctl0:ContentPlaceHolder1:ddlTables': '6b',
                                       '_ctl0:ContentPlaceHolder1:ddlSocialGroup': '4',
                                       '_ctl0:ContentPlaceHolder1:ddlCrop': crop[1],
                                       '_ctl0:ContentPlaceHolder1:btnSubmit': 'Submit'
                                       }

                    # req_taluk_char = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                    #                               data=data_post_taluk,
                    #                               headers=headers_url, allow_redirects=False)

                    # req_taluk_char = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                    #                               data=data_post_taluk,
                    #                               headers=headers_url, allow_redirects=False)
                    # print(req_taluk_char.status_code)
                    # print(req_taluk_char.text)

                    taluk_char = requests.Request('POST',
                                                  "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                                                  headers=headers_url,
                                                  data=data_post_taluk)
                    prepped_taluk_char = taluk_char.prepare()
                    response_taluk_char = try_request(prepped_taluk_char)

                    tk_table_get = requests.Request("GET",
                                                    "https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                                                    headers=headers_url)
                    prepped_tk_table_get = session.prepare_request(tk_table_get)
                    response_tk_table_get = try_request(prepped_tk_table_get,
                                                        is_eventval_request=True)
                    # response_tk_table_get = session.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                    #                                headers=headers_url)
                    # print(response_tk_table_get.text)

                    # req_tk_table_get = session.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                    #                                headers=headers_url)

                    tktable_get_soup = BeautifulSoup(response_tk_table_get.text, "html.parser")

                    event_validation = tktable_get_soup.select("#__EVENTVALIDATION")[0]['value']
                    new_view_state = tktable_get_soup.select("#__VIEWSTATE")[0]['value']
                    new_view_state_gen = tktable_get_soup.select("#__VIEWSTATEGENERATOR")[0]['value']

                    tk_data = {"__EVENTTARGET": "ReportViewer1$_ctl9$Reserved_AsyncLoadTarget",
                               '__EVENTARGUMENT': "",
                               "__VIEWSTATE": new_view_state,
                               '__VIEWSTATEGENERATOR': new_view_state_gen,
                               '__VIEWSTATEENCRYPTED': "",
                               "__EVENTVALIDATION": event_validation,
                               "ReportViewer1:_ctl3:_ctl0": "",
                               "ReportViewer1:_ctl3:_ctl1": "",
                               "ReportViewer1:_ctl10": "ltr",
                               "ReportViewer1:_ctl11": "standards",
                               "ReportViewer1:AsyncWait:HiddenCancelField": "False",
                               "ReportViewer1:ToggleParam:store": "",
                               "ReportViewer1:ToggleParam:collapse": "false",
                               "ReportViewer1:_ctl8:ClientClickedId": "",
                               "ReportViewer1:_ctl7:store": "",
                               "ReportViewer1:_ctl7:collapse": "false",
                               "ReportViewer1:_ctl9:VisibilityState:_ctl0": "None",
                               "ReportViewer1:_ctl9:ScrollPosition": "",
                               "ReportViewer1:_ctl9:ReportControl:_ctl2": "",
                               "ReportViewer1:_ctl9:ReportControl:_ctl3": "",
                               "ReportViewer1:_ctl9:ReportControl:_ctl4": "100"
                               }
                    # req_tk_table_post = session.post("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                    #                                  headers=headers_url,
                    #                                  data=tk_data)

                    tk_table_post = requests.Request('POST',
                                                     "https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                                                     headers=headers_url,
                                                     data=tk_data)
                    prepped_post_taluk = session.prepare_request(tk_table_post)
                    response_tk_table_post = try_request(prepped_post_taluk, is_table_request=True)

                    name = save_file(response_tk_table_post.text)
                    if name == -1:
                        log("no record for " + gen_file_name())
                        file_name_unsuccessful = gen_file_name()
                        record_file(state[0], file_name_unsuccessful, False)
                        continue
                    result_upload = upload_file("saved_tables/" + name)
                    if result_upload == -1:
                        file_name_unsuccessful = gen_file_name()
                        log("unable to upload file to dropbox, " + file_name_unsuccessful)
                        record_file(state[0], file_name_unsuccessful, upload_problem=True)
                        continue
                    time.sleep(CRAWLER_DELAY)

                # done with tehsil, mark as done
                mark_done(str(year), state[0], district[0], tehsil[0])

# make log file: time of error, what happened
# have backoff policy
# two kinds of errors: data not available and website failed
