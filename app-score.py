#!/usr/bin/env python3

import prisma_sase
import io
import requests
import json
import csv
import time
import os
import termtables as tt
import yaml
import argparse

global tsg

def sdk_login_to_controller(filepath):
    with open(filepath) as f:
        client_secret_dict = yaml.safe_load(f)
        client_id = client_secret_dict["client_id"]
        client_secret = client_secret_dict["client_secret"]
        tsg_id_str = client_secret_dict["scope"]
        global tsg
        tsg = tsg_id_str.split(":")[1]
        #print(client_id, client_secret, tsg)

    global sdk 
    sdk = prisma_sase.API(controller="https://sase.paloaltonetworks.com/", ssl_verify=False)
   
    sdk.interactive.login_secret(client_id, client_secret, tsg)
    #print("--------------------------------")
    #print("Script Execution Progress: ")
    #print("--------------------------------")
    #print("Login to TSG ID {} successful".format(tsg))



def create_csv_output_file(Header, RList):
    with open('tunnel-status.csv', mode='w') as csv_file:
        csvwriter = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(Header)
        for Rec in RList:
            csvwriter.writerow(Rec)

def create_json_output_file():
    #create a dictionary
    data_dict = {}
 
    with open('tunnel-status.csv', encoding = 'utf-8') as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        i=0
        for rows in csv_reader:
            key = i
            data_dict[key] = rows
            i += 1
 
    with open('tunnel-status.json', 'w', encoding = 'utf-8') as json_file_handler:
        json_file_handler.write(json.dumps(data_dict, indent = 4))

def fetch_user_list_below_exp_score(expScore, days):
    #endpoints (agent_uuid), users where experience score averaged over all tests is < expScore ( poor,fair,good is 30, 70, 100 ) 
    
    last_n_days_str = "last_"+ str(days)+ "_days"
    if expScore<30:
        exp_score_str = "poor"
    elif expScore >=30 and expScore<70:
        exp_score_str = "poor,fair"
    else:
        exp_score_str = "poor,fair,good"
   
    final_collection_list = [] 
    page_num = 0
    data_found = True
    
    while True:
        collection_list = []
        pagination_str = "&pagination=page=="+str(page_num)+";limit==50;sortBy==application;sortOrder==asc"
        url = "https://api.sase.paloaltonetworks.com/adem/telemetry/v2/measure/agent/score?timerange="+last_n_days_str+"&group=en.user,en.endpoint&endpoint-type=muAgent&result-filter=Score.application=="+exp_score_str+"&response-type=grouped-summary"+pagination_str
        header = {
               "prisma-tenant": tsg
        }
        sdk._session.headers.update(header)

        resp = sdk.rest_call(url=url, method="GET")
        try:
            pass
            #prisma_sase.jd_detailed(resp)
        except:
            print("No data found.")
            break
   
    
        #print(resp.json()) 
        resp = resp.json()
        try: 
            collection_list = resp["collection"]
            final_collection_list += collection_list
            #print(collection_list)
            if collection_list == []:
                break
        except:
            print("No ADEM Data found for users with experience score less than {} for the past {} days".format(exp_score_str, days))
            break  
        
        page_num += 1

    Header = ["Users", "Experience Score"]
    RList = []
    index = 0
    for collection in final_collection_list:
        #print(collection)
        user = collection["id"]["user"]
        experience_score_collection = collection["average"]["application"]
        if experience_score_collection <= expScore: 
            RList.append([user, str(experience_score_collection)])

    if RList != []:
        create_csv_output_file(Header,RList)
        create_json_output_file()

        table_string = tt.to_string(RList, Header, style=tt.styles.ascii_thin_double)
        print(table_string)

def go():
    parser = argparse.ArgumentParser(description='Retrieve all end users with devices that have less than a given Experience Score .')
    parser.add_argument('-t1', '--T1Secret', help='Input secret file in .yml format for the tenant(T1) ',default="T1-secret.yml")
    parser.add_argument('-expScore', '--expScore', help='Experience score threshold below which the users will be listed ',default='all')  
    parser.add_argument('-days', '--Days', help='Data fetched for the last n days ',default=30)

    args = parser.parse_args()
    T1_secret_filepath = args.T1Secret
    expScore = args.expScore
    days = int(args.Days)

    #Pass the secret of 'from tenant' to login
    sdk_login_to_controller(T1_secret_filepath)

    #ADEM APIs to fetch user list with experience score below a given value
    fetch_user_list_below_exp_score(int(expScore), days)

if __name__ == "__main__":
    go()
