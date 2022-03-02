# - For year in [2001, 2015, 2016, 2005, 2010]:
#   - Create session
#   - Make call to homepage, get ViewState info
#   - Make call to Get_ddlData (returns list of states for that year)
#   - Parse list of states to get districts (or make call to getDistrict with the state)
#   - For each district:
#     - Make call to getTehsil (returns list of tehsils)
#     - For each tehsil:
#       - For each crop in [paddy, wheat, maize, soybean, cotton, groundnut, rapeseed and mustard, bajra, sugarcane, jowar]:
#         - Make POST to GetSession with form data
#         - Make POST to homepage with ViewState info
#         - Make GET to tktabledisplay to get EventValidation info
#         - Make POST to tktabledisplay, get table back
#           - Or error back if no data
#         - Parse table contents
#         - Save to file
#
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
from upload_dropbox import Uploader
from interface_trackers import get_finished_set, get_last_done, mark_done

# TODO: separate out into functions
# TODO: documentation
# TODO: don't forget to switch years back to full list


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
    initial = soup.find("div", text="Sl No")
    if initial is None:
        return -1

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
            row_data.append(col.get_text)
        row_data = row_data[1:]
        data.append(row_data)
        row_number += 1

    df = pd.DataFrame(data=data, columns=headers)
    file_name = str(year) + "_" + state[0] + "_" + district[0] + "_" + tehsil[0] + "_" + crop[0] + ".csv"
    df.to_csv(file_name)
    return file_name


def upload_file(path):
    res = uploader.upload(path)
    if res != 0:
        print("uh oh, something went wrong")


def check_already_done(check_year, check_state, check_district, check_tehsil, check_crop):
    if (str(check_year), check_state.strip(), check_district.strip(), check_tehsil.strip(), check_crop) in finished:
        return True
    return False



years = [2000]
years_text = ["2000-01"]
crops = [("PADDY", "101"), ("WHEAT", "106"), ("MAIZE", "104"), ("SOYABEAN", "1009"), ("COTTON", "1101"),
         ("GROUNDNUT", "1001"),
         ("RAPESEED & MUSTARD", "1004"), ("BAJRA", "103"), ("SUGARCANE", "401"), ("JOWAR", "102")]
session = requests.Session()
crawler_delay = 5

headers_json = {'Content-Type': "application/json; charset=utf-8"}
headers_url = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate, br",
               "Content-Type": "application/x-www-form-urlencoded",
               "Connection": "keep-alive",
               }

uploader = Uploader()
finished = get_finished_set()
last_done = get_last_done()


for i in range(len(years)):
    year = years[i]
    year_text = years_text[i]

    if last_done["year"] >= year:
        continue

    # get home page
    req_home = session.get("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx")

    # parse w BS4
    home_html = req_home.text
    home_soup = BeautifulSoup(home_html, 'html.parser')

    # parse viewstate
    # TODO: check if this is null
    view_state = None if home_soup.select("#__VIEWSTATE") is None else home_soup.select("#__VIEWSTATE")[0]['value']
    view_state_gen = None if home_soup.select("#__VIEWSTATEGENERATOR") is None else \
        home_soup.select("#__VIEWSTATEGENERATOR")[0]['value']

    if view_state_gen is None or view_state is None:
        print("unable to parse viewstate")
        exit()

    # get states available for this year
    data_ddl = json.dumps({'value': str(year), 'Text': year_text, 'CallFor': 'Year'})
    req_get_ddl = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/Get_ddlData",
                               headers=headers_json,
                               data=data_ddl)

    json_response_ddl = req_get_ddl.json()
    states_for_year = json_response_ddl['d']['State']
    states = parse_list(states_for_year)

    for state in states:
        if last_done["state"] >= state:
            continue
        # get districts for this state
        print("handling state " + str(state))
        data_district = json.dumps({'value': state[1], 'Text': state[0], 'CallFor': 'State', 'year': str(year)})
        req_get_district = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getDistrict",
                                        headers=headers_json,
                                        data=data_district)
        json_response_district = req_get_district.json()
        districts_for_state = json_response_district['d']['District']
        print(districts_for_state)
        districts = parse_list(districts_for_state)
        print(districts)
        for district in districts:
            if last_done["district"] >= district:
                continue
            # get tehsils for this district
            print("handling district " + str(district))
            data_tehsil = json.dumps(
                {'value': district[1], 'Text': district[0], 'CallFor': 'District', 'stcdu': state[1],
                 'year': str(year)})
            req_get_tehsil = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getTehsil",
                                          headers=headers_json,
                                          data=data_tehsil)
            # TODO: wrap in try/catch
            json_response_tehsil = req_get_tehsil.json()
            tehsils_for_district = json_response_tehsil['d']['Tehsil']
            tehsils = parse_list(tehsils_for_district)
            print(tehsils)
            for tehsil in tehsils:
                # check if cropping pattern is available
                print("handling tehsil " + str(tehsil))
                data_crop = json.dumps(
                    {'year': year, 'State': state[1], 'Level': 'TehsilLevel', 'District': district[1],
                     'Tehsil': tehsil[1]})
                # try:
                req_get_crop = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/Get_Crop",
                                            headers=headers_json,
                                            data=data_crop)
                print("here")
                print(req_get_crop.json())
                text_response_crop = req_get_crop.json()['d']['Crops']
                if text_response_crop == "":
                    print("no cropping pattern data for tehsil " + str(tehsil[0]) + " in year " + str(year))
                    continue
                for crop in crops:
                    if crop[0] not in text_response_crop:
                        print("crop " + str(crop[0]) + " data not available for tehsil " + str(
                            tehsil[0]) + " in year " + str(year))
                        continue
                    # check if should continue
                    if check_already_done(year, state[0], district[0], tehsil[0], crop[0]):
                        continue

                    data_get_session = json.dumps({
                        "value1": [year_text, str(year), "CROPPING PATTERN", "6b", "ALL SOCIAL GROUPS", "4", crop[0],
                                   crop[1], state[0], state[1],
                                   district[1], "1", "CIVIL LINES", "1"]})

                    req_get_session = session.post(
                        "https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession",
                        headers=headers_json,
                        data=data_get_session)
                    if req_get_session.status_code != 200:
                        # TODO: handle error case
                        continue

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
                    req_taluk_char = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                                                  data=data_post_taluk,
                                                  headers=headers_url, allow_redirects=False)
                    # TODO: check status code
                    req_tk_table_get = session.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                                                   headers=headers_url)

                    tktable_get_soup = BeautifulSoup(req_tk_table_get.text, "html.parser")
                    # TODO: check that this is not null
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
                    req_tk_table_post = session.post("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                                                     headers=headers_url,
                                                     data=tk_data)
                    print(req_tk_table_post.text)
                    name = save_file(req_tk_table_post.text)
                    if name == -1:
                        # TODO: log error
                        continue
                    upload_file(name)
                    time.sleep(crawler_delay)

            # done with district, mark as done
            mark_done(year, state[0], district[0])



# make log file: time of error, what happened
# have backoff policy
# two kinds of errors: data not available and website failed
