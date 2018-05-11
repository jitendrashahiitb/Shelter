''''
Script to transfer data from one form to other.
 format.json - JSON format that is accepted by the new form.
 direct_mapping.json - JSON format - Fields that are directly mapped from new form to old form
 
To run include the folder in sys path

import sys
sys.path.insert(0, 'scripts/K2KMigration/')
from migrate import *
queryToFetchRecords(kobo_survey)
'''

import uuid
from django.conf import settings
import json
import urllib2
import itertools
import os
import dicttoxml
import xml.etree.ElementTree as ET
import commentjson
from bs4 import BeautifulSoup
import re
import datetime
                              # Version                 #formhubid                        #id_string
kobo_survey = "54" # PCMC_RHS   #vvik5wDuJ5CcmVPBGrHX6v #b264f76a98e04ee6b4cf0f9d6823540a  #afYDtpdPK8yUVjFNZkMR7q
#kobo_survey = "53" # Thane_RHS  #vHcmNweMUZbipF9c9cWC2b #931938b11d32433d89ef6005ff22bc91 #atQTvzHaChfdUdvtvnJKkg
#kobo_survey = "65" # NMMC_RHS
#132
root_folder_path = os.path.dirname(os.path.abspath(__file__))
root_output_folder = os.path.join(root_folder_path, 'xml_output')
output_folder_path = os.path.join(root_output_folder, 'PCMC', 'RHS')
DOUBLE_HOUSE = {"272537891001":{"27":"124"},
                "272537892501":{ "216":"217","809":"808","813":"812","841":"840","878":"877","479":"477","566":"567","669":"665","1488":"1489","1618":"1617","1807":"1806"},
                "272537892702":{"49":"50","80":"79","248":"249"},
                "272537891003":{"56":"55","70":"71","118":"117","223":"222"},
                "272537891801":{"221":"222","223":"222","251":"250","275":"274","430":"429","445":"443","531":"533"},
                "272537892704":{"135":"136"},
                "272537890802":{"216":"217","219":"218"},
                "272537891004":{"205":"202","217":"216","232":"231"},
                "272537891802":{"5":"4","18":"17","45":"46","47":"46","48":"49","76":"81","80":"85"},
                "272537890804":{"362":"361","808":"810","1077":"1072"},
                "272537895301":{"38":"36","90":"91","265":"263"},
                "272537894202":{"57":"56","104":"103","313":"312","326":"325","375":"376"},
                "272537894203":{"156":"155","244":"243"},
                "272537895202":{"501":"500","514":"515","517":"515","529":"530","531":"532","537":"535","583":"582","584":"582","591":"590","592":"590","595":"593","597":"596"},
                "272537894204":{"14":"13","303":"302"},
                "272537895302":{"2":"1","12":"11","20":"21","57":"56","58":"56","73":"74","76":"75","88":"87","91":"90","98":"97","206":"205","207":"208"},
                "272537894206":{"68":"63","117":"118","317":"316","369":"368"},
                "272537892104":{"253":"251","382":"381"},
                "272537894310":{"7":"6"},
                "272537893801":{"86":"87"},
                "272537894001":{"256":"255","274":"273","300":"299","394":"393","511":"508","550":"542","1310":"1309","1382":"1381"},
                "272537896101":{"461":"460","526":"524","531":"529","677":"683"},
                "272537896201":{"44":"42"},
                "272537893702":{"564":"563","666":"661","742":"741","767":"766"},
                "272537893703":{"1143":"1144","1219":"1221","1289":"1288","1318":"1319","1320":"1321","1597":"1598","1649":"1651","1668":"1662","1763":"1762","1794":"1793"},
                "272537896401":{"361":"358","446":"447","460":"461","721":"722","757":"756","767":"768","816":"819"},
                "272537896204":{"124":"122","171":"177","611":"610"},
                "272537896402":{"472":"473","615":"614","711":"710","725":"724","891":"890"},
                "272537893802":{"270":"273","348":"345","460":"461"},
                "272537894304":{"78":"77"},
                "272537894306":{"51":"52"},
                "272537894501":{"246":"245"},
                "272537894309":{"286":"285"},
                "272537892902":{"454":"453"},
                "272537892903":{"339":"340","349":"350","354":"353"},
                "272537890601":{"38":"37","56":"55","97":"95","122":"121","153":"152","229":"228","326":"327"},
                "272537893601":{"183":"180","212":"211","317":"316","396":"397"},
                "272537890401":{"373":"374","383":"384","679":"686","760":"761"}
                }
def rhs_form():
    format = open(os.path.join(root_folder_path, 'format.json'), 'rw')
    return commentjson.loads(format.read())

def mapping_form():
    direct_mapping = open(os.path.join(root_folder_path, 'direct_mapping.json'), 'rw')
    return commentjson.loads(direct_mapping.read())

def queryToFetchRecords(kobo_survey):
    print "Start fetching the details"
    date_now = datetime.datetime.now()
    rec=[]
    #slum_code = '273425262402'
    #url = settings.KOBOCAT_FORM_URL + 'data/' + kobo_survey + '?format=json&query={"group_ce0hf58/slum_name":"' + slum_code + '"}'
    url = settings.KOBOCAT_FORM_URL + 'data/' + kobo_survey + '?format=json&query={ "_id":{"$lte":123957}}'
    #url = settings.KOBOCAT_FORM_URL + 'data/' + kobo_survey + '?format=json'
    kobotoolbox_request = urllib2.Request(url)
    kobotoolbox_request.add_header('User-agent', 'Mozilla 5.10')
    kobotoolbox_request.add_header('Authorization', settings.KOBOCAT_TOKEN)
    res = urllib2.urlopen(kobotoolbox_request)
    html = res.read()
    json_records = json.loads(html)

    url = settings.KOBOCAT_FORM_URL + 'data/' + kobo_survey + '?format=json&query={ "_id":{"$gt":123957}}'
    kobotoolbox_request = urllib2.Request(url)
    kobotoolbox_request.add_header('User-agent', 'Mozilla 5.10')
    kobotoolbox_request.add_header('Authorization', settings.KOBOCAT_TOKEN)
    res = urllib2.urlopen(kobotoolbox_request)
    html = res.read()
    json_records.extend(json.loads(html))

    for record in json_records:
        if 'group_ye18c77/group_yw8pj39/what_is_the_structure_of_the_house' in record and record['group_ye18c77/group_yw8pj39/what_is_the_structure_of_the_house'] !="":
            record["group_ce0hf58/Type_of_structure_occupancy"] = "01"

    print (url)
    print ("Total count :- "+str(len(json_records)))
    grouped_records = itertools.groupby(sorted(json_records, key=lambda x: x['group_ce0hf58/slum_name']),
                                        key=lambda x: x["group_ce0hf58/slum_name"])
    records = {}
    for list_record in grouped_records:
        slum_house = list(list_record[1])
        grouped_house_records = itertools.groupby(sorted(slum_house, key=lambda x: int(x['group_ce0hf58/house_no'])),
                                            key=lambda x: int(x["group_ce0hf58/house_no"]))
        house = {}
        for list_house in grouped_house_records:
            house[list_house[0]] = list(list_house[1])

        records[list_record[0]] = house


    for k,v in records.iteritems():
      slum_code = k
      print ("Slum - "+str(k) + "("+str(len(v.keys()))+")")
      date_slum = datetime.datetime.now()
      folder_path = os.path.join(output_folder_path, "slum_" + str(slum_code.replace('/', '')))
      for key,val in v.iteritems():
        #print ("\t" + str(key))
        record_sorted = sorted(val, key=lambda x: x['end'], reverse=True)
        flag=True
        for record_sort in record_sorted:
            if 'group_ce0hf58/Type_of_structure_occupancy' in record_sort:
              if record_sort['group_ce0hf58/Type_of_structure_occupancy'] == "01" or (record_sort['group_ce0hf58/Type_of_structure_occupancy']!= "01" and flag):
                flag = False
                record = record_sort
                #record = record_sorted[0]
                create_data = rhs_xml_create(record)

                status, replace_data = kmc_rhs_xml_replace(create_data, record)

                if status:
                    xml_string = create_xml_string(replace_data, [], replace_data['_xform_id_string'], replace_data['_xform_id_string'],
                                                   replace_data['__version__'])
                    file_name = 'RHS_Survey_Slum_Id_' + str(slum_code.replace('/', '')) + '_House_code_' + str(key) +'_'+str(record['_id'])

                    create_xml_file(xml_string, file_name, folder_path)
      print "Slum time" + str(datetime.datetime.now() - date_slum)
    print "Total time" + str(datetime.datetime.now() - date_now)
    return rec

def rhs_xml_create(xml_record):
    gl_rhs_xml_dict = rhs_form()
    mapping =  mapping_form()
    for key, val in xml_record.iteritems():
        key = str(key)
        if not key.startswith('_'):
            split_ky = key.split('/')
            if split_ky[len(split_ky)-1] in mapping.keys():
                split_key = mapping[split_ky[len(split_ky)-1]].split('/')
                if len(split_key) == 1:
                    gl_rhs_xml_dict[split_key[0]] = val
                if len(split_key) == 2:
                    gl_rhs_xml_dict[split_key[0]][split_key[1]] = val
                if len(split_key) == 3:
                    gl_rhs_xml_dict[split_key[0]][split_key[1]][split_key[2]] = val
                if len(split_key) == 4:
                    gl_rhs_xml_dict[split_key[0]][split_key[1]][split_key[2]][split_key[3]] = val

    return gl_rhs_xml_dict

UNOCCUPIED_HOUSE = {"03" : "021", "04":"022", "05":"023", "06":"024", "07":"025"}
FACILITY_OF_SOLID_WASTE = {"01":"04", "02":"01", "03":"02", "04":"03", "05":"04", "06":"05", "07":"06"}
i=0
def kmc_rhs_xml_replace(rhs_record, record):
    flag=False
    '''Replacement for the records
    '''
    #rhs_record['meta']['deprecatedID'] = rhs_record['meta']['instanceID']
    global i
    rhs_record['Enter_household_number_again'] = record['group_ce0hf58/house_no']
    rhs_record['meta']['instanceID'] = 'uuid:' + str(uuid.uuid4())
    # RHS section
    if record['group_ce0hf58/Type_of_structure_occupancy'] in ["03","04","05","06","07"]:
        rhs_record['Type_of_structure_occupancy'] = "02"
        rhs_record['Type_of_unoccupied_house'] = UNOCCUPIED_HOUSE[record['group_ce0hf58/Type_of_structure_occupancy']]
    else:
        rhs_record['Type_of_structure_occupancy'] = "03" if record['group_ce0hf58/Type_of_structure_occupancy']=="02" else "01"

    if rhs_record['Type_of_unoccupied_house'] and rhs_record['Type_of_unoccupied_house'] == "021":# and 'group_ye18c77/group_ud4em45/what_is_the_full_name_of_the_family_head_' in record :

        parent_house = (record['group_ye18c77/group_ud4em45/what_is_the_full_name_of_the_family_head_'].strip())#.split(' ')
        #print record['group_ye18c77/group_ud4em45/what_is_the_full_name_of_the_family_head_']
        if re.search('[0-9]+',parent_house) != None:
            rhs_record['Parent_household_number'] = int(re.search('[0-9]+',parent_house).group(0))
        else:
            if rhs_record['slum_name'] in DOUBLE_HOUSE.keys() and str(rhs_record['Household_number']) in DOUBLE_HOUSE[rhs_record['slum_name']].keys():
                i=i+1
                print str(i)
                rhs_record['Parent_household_number'] = int(DOUBLE_HOUSE[rhs_record['slum_name']][str(rhs_record['Household_number'])])
        if rhs_record['Parent_household_number'] == 0:
            rhs_record['Parent_household_number'] = None

    if rhs_record['Type_of_structure_occupancy'] != "01":
        rhs_record['group_el9cl08']['Type_of_water_connection'] =""
        rhs_record['group_el9cl08']['Enter_the_10_digit_mobile_number'] = ""
        rhs_record['group_el9cl08']['Aadhar_number'] = ""
        rhs_record['group_og5bx85']['Full_name_of_the_head_of_the_household'] = ""

    if rhs_record['group_el9cl08']['Enter_the_10_digit_mobile_number'] and not re.search('^[0-9]{10}$|^[0-9]{12}$',
                                                                                         rhs_record[
                                                                                             'group_el9cl08'][
                                                                                             'Enter_the_10_digit_mobile_number']):
        rhs_record['group_el9cl08']['Enter_the_10_digit_mobile_number'] = ""

    if rhs_record['group_el9cl08']['Aadhar_number'] and not re.search('^[0-9]{12}$',
                                                                      rhs_record['group_el9cl08']['Aadhar_number']):
        rhs_record['group_el9cl08']['Aadhar_number'] = ""

    if rhs_record['Type_of_structure_occupancy'] == "01":
        rhs_record['group_og5bx85']['Type_of_survey'] = "01"

        # if not rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi']:
        #     rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi'] = '02'

        # if not rhs_record['group_el9cl08']['Type_of_structure_of_the_house']:
        #     rhs_record['group_el9cl08']['Type_of_structure_of_the_house'] = '02'

        # if not rhs_record['group_el9cl08']['Ownership_status_of_the_house']:
        #     rhs_record['group_el9cl08']['Ownership_status_of_the_house'] = '02'
        #
        # if not rhs_record['group_el9cl08']['Does_any_household_m_n_skills_given_below']:
        #     rhs_record['group_el9cl08']['Does_any_household_m_n_skills_given_below'] ='05'

        if rhs_record['group_el9cl08']['Number_of_household_members'] and int(
                rhs_record['group_el9cl08']['Number_of_household_members']) > 20:
            #print "Number of members" + rhs_record['group_el9cl08']['Number_of_household_members']
            rhs_record['group_el9cl08']['Number_of_household_members'] = 5

        if rhs_record['group_el9cl08']['Number_of_household_members'] and int(
                rhs_record['group_el9cl08']['Number_of_household_members']) == 0:
            rhs_record['group_el9cl08']['Number_of_household_members'] = 5

        if rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi'] == "01" and int(rhs_record['group_el9cl08']['How_many']) == 0:
            rhs_record['group_el9cl08']['How_many'] = None
            rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi'] = "02"

        if rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi'] == "01" and int(
                rhs_record['group_el9cl08']['How_many']) >= 10:
            rhs_record['group_el9cl08']['How_many'] = 3

        if rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi'] == "02" and rhs_record['group_el9cl08']['How_many'] and int(
                rhs_record['group_el9cl08']['How_many']) > 0:
            rhs_record['group_el9cl08']['Do_you_have_any_girl_child_chi'] = "01"

        if rhs_record['group_oi8ts04']['How_many_installments_have_you'] and (not rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] or rhs_record['group_oi8ts04']['Have_you_applied_for_individua']=="02"):
            #print "Changed to yes for individual SBM applied"
            rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "01"

        if 'group_ye18c77/group_yw8pj39/house_area_in_sq_ft' in record:
            val = int(record['group_ye18c77/group_yw8pj39/house_area_in_sq_ft'])
            if val < 100:
                rhs_record['group_el9cl08']['House_area_in_sq_ft'] = "01"
                #print "01"
            elif 100 <= val < 200 :
                rhs_record['group_el9cl08']['House_area_in_sq_ft'] = "02"
                #print "02"
            elif 200 <= val < 300:
                rhs_record['group_el9cl08']['House_area_in_sq_ft'] = "03"
                #print "03"
            elif 300 <= val < 400:
                rhs_record['group_el9cl08']['House_area_in_sq_ft'] = "04"
                #print "04"
            elif val >= 400:
                rhs_record['group_el9cl08']['House_area_in_sq_ft'] = "05"
                #print "05"
        waste_facility =[]

        if 'group_ye18c77/group_yw8pj39/facility_of_waste_collection' in record and len(record['group_ye18c77/group_yw8pj39/facility_of_waste_collection'].split(' ')) > 0:
            #for waste_collection in record['group_ye18c77/group_yw8pj39/facility_of_waste_collection'].split(' '):
            #    waste_facility.append(FACILITY_OF_SOLID_WASTE[waste_collection])
            rhs_record['group_el9cl08']['Facility_of_solid_waste_collection'] = FACILITY_OF_SOLID_WASTE[record['group_ye18c77/group_yw8pj39/facility_of_waste_collection'].split(' ')[0]]#' '.join(waste_facility)

        # RHS and follow up survey data
        #Need to check after migration ------------- ******
        if not rhs_record['group_oi8ts04']['Have_you_applied_for_individua']:
            rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "02"

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01" and (not rhs_record['group_oi8ts04']['How_many_installments_have_you'] or rhs_record['group_oi8ts04']['How_many_installments_have_you'] == ""):
            #print "Hello"
            rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = '02'

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01":
            rhs_record['group_oi8ts04']['Type_of_SBM_toilets'] = "01"

        TOILET_UNDER_SBM = {"01": "01", "02": "03", "03": "04", "04": "05"}
        if 'group_ye18c77/group_yw8pj39/what_is_the_status_of_toilet_under_sbm_' in record:
            rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = TOILET_UNDER_SBM[
                record['group_ye18c77/group_yw8pj39/what_is_the_status_of_toilet_under_sbm_']]

        TOILET_PREFERENCE = {"01": "01", "02": "02", "03": "02", "04": "02"}
        if 'group_ye18c77/group_yw8pj39/type_of_toilet_preference' in record:
            rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = TOILET_PREFERENCE[record[
                'group_ye18c77/group_yw8pj39/type_of_toilet_preference']]

        TOILET_CONNECTED_TO = {"01": "01", "02": "02", "03": "03", "04": "04", "05": "05", "06": "06", "07": "08",
                               "08": "08", "09": "07"}
        if 'group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_' in record:
            rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = TOILET_CONNECTED_TO[
                record['group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_']]

        OPEN_DEFECATION = {"01": "01", "02": "02", "03": "04", "04": "05"}
        if 'group_ye18c77/group_yw8pj39/does_any_member_of_your_family_go_for_open_defecation_' in record:
            rhs_record['group_oi8ts04']['OD1'] = OPEN_DEFECATION[
                record['group_ye18c77/group_yw8pj39/does_any_member_of_your_family_go_for_open_defecation_']]
        ##### NEW
        else:
            if "07" in record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet']:
                rhs_record['group_oi8ts04']['OD1'] = "05"
            else:
                rhs_record['group_oi8ts04']['OD1'] = "01"
        #####

        if not rhs_record['group_el9cl08']['Does_any_household_m_n_skills_given_below']:
            rhs_record['group_el9cl08']['Does_any_household_m_n_skills_given_below'] = "05"

        DEFECATION = {"01": "05", "02": "05", "03": "09", "04": "10", "05": "11", "07": "12"}
        if rhs_record['group_oi8ts04']['When_did_you_receive_r_second_installment']:
            rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "01"
            if rhs_record['group_oi8ts04']['How_many_installments_have_you'] != "03":
                rhs_record['group_oi8ts04']['How_many_installments_have_you'] = "03"

            if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "01":
                rhs_record['group_oi8ts04']['C1'] = "01"
                if not rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to']:
                    rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"

            if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] in ["03","04"]:
                c2 = None
                defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                c2 = DEFECATION[defecation[0]]
                if c2 == "05":
                    c2 = "09"
                rhs_record['group_oi8ts04']['C4'] = c2
                rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = None

            if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "05":
                defecation = DEFECATION[record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()[0]]
                if defecation == "05":
                    rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = "01"
                    rhs_record['group_oi8ts04']['C1'] = "01"
                else:
                    rhs_record['group_oi8ts04']['C4'] = defecation

            if not rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM']:
                defecation = DEFECATION[record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()[0]]
                if defecation == "05":
                    rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = "01"
                    rhs_record['group_oi8ts04']['C1'] = "01"
                    if not rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to']:
                        rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"
                    rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                    rhs_record['group_oi8ts04']['If_no_why'] = None
                    rhs_record['group_oi8ts04']['If_yes_why'] = None
                else:
                    rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] ="04"
                    rhs_record['group_oi8ts04']['C4'] = defecation
                    rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                    rhs_record['group_oi8ts04']['If_no_why'] = None
                    rhs_record['group_oi8ts04']['If_yes_why'] = None

        if not rhs_record['group_oi8ts04']['When_did_you_receive_r_second_installment'] and rhs_record['group_oi8ts04']['When_did_you_receive_ur_first_installment']:
            if not rhs_record['group_oi8ts04']['Have_you_applied_for_individua']:
                rhs_record['group_oi8ts04']['Have_you_applied_for_individua']= "01"

            if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "01":
                rhs_record['group_oi8ts04']['C1'] = "01"
                if not rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to']:
                    rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"

            if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] in ["03", "04"]:
                c2 = None
                defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                c2 = DEFECATION[defecation[0]]
                if c2 == "05":
                    c2 = "09"
                rhs_record['group_oi8ts04']['C4'] = c2
                rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = None
                rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                rhs_record['group_oi8ts04']['If_no_why'] = None
                rhs_record['group_oi8ts04']['If_yes_why'] = None
                rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None

            if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "05":
                c2 = None
                defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                c2 = DEFECATION[defecation[0]]
                if c2 == "05":
                    c2 = "09"
                rhs_record['group_oi8ts04']['C4'] = c2
                rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = None
                rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                rhs_record['group_oi8ts04']['If_no_why'] = None
                rhs_record['group_oi8ts04']['If_yes_why'] = None
                rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None

        if not rhs_record['group_oi8ts04']['When_did_you_receive_r_second_installment'] and not rhs_record['group_oi8ts04']['When_did_you_receive_ur_first_installment']:
            if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "02":
                if not rhs_record['group_oi8ts04']['How_many_installments_have_you'] and not rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] or rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] =="05":
                    c2 = None
                    rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = None
                    rhs_record['group_oi8ts04']['How_many_installments_have_you'] = None
                    defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                    c2 = DEFECATION[defecation[0]]
                    if c2 != "05":
                        rhs_record['group_oi8ts04']['C2'] = "08"
                        rhs_record['group_oi8ts04']['C3'] = c2
                    else:
                        rhs_record['group_oi8ts04']['C2'] = c2
                    if 'group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_' in record and record['group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_'] =="07":
                        c2 = "13"
                        rhs_record['group_oi8ts04']['C2'] = c2
                        rhs_record['group_oi8ts04']['C3'] = None
                        rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] ="08"
                    if c2 == "05":
                        if not rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to']:
                            rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"
                        rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                        rhs_record['group_oi8ts04']['If_no_why'] = None
                        rhs_record['group_oi8ts04']['If_yes_why'] = None
                        rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None
                    if c2 != "05" and c2 != "13":
                        rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to']  = None
                        if not rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] :
                            rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = "02"
                            if not rhs_record['group_oi8ts04']['If_no_why']:
                                rhs_record['group_oi8ts04']['If_no_why'] ="08"
            flag= False
            if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01":
                if rhs_record['group_oi8ts04']['How_many_installments_have_you'] == "02":
                    rhs_record['group_oi8ts04']['How_many_installments_have_you'] = "01"

                if not rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM']:
                    rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "02"
                    rhs_record['group_oi8ts04']['How_many_installments_have_you'] = None
                    c2 = None
                    defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                    c2 = DEFECATION[defecation[0]]
                    if c2 != "05":
                        rhs_record['group_oi8ts04']['C2'] = "08"
                        rhs_record['group_oi8ts04']['C3'] = c2
                    else:
                        rhs_record['group_oi8ts04']['C2'] = c2
                        if 'group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_' in record and record['group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_'] == "07":
                            c2 = "13"
                            rhs_record['group_oi8ts04']['C2'] = c2
                            rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"

                if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] in ["01", "03", "04"]:
                    c2 = None
                    defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                    c2 = DEFECATION[defecation[0]]
                    if c2 != "05":
                        rhs_record['group_oi8ts04']['C5'] = c2
                        rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = "05"
                        rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = "02"
                        if not rhs_record['group_oi8ts04']['If_no_why']:
                            rhs_record['group_oi8ts04']['If_no_why'] = "08"

                    else:
                        flag=True
                        #print "03 :" +str(record['group_ce0hf58/house_no'])
                        rhs_record['group_oi8ts04']['How_many_installments_have_you'] = None
                        rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "03"
                        rhs_record['group_oi8ts04']['Type_of_SBM_toilets'] = None
                        rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = None
                        rhs_record['group_oi8ts04']['C2'] = c2
                        if 'group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_' in  record and record['group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_'] == "07":
                            c2 = "13"
                            rhs_record['group_oi8ts04']['C2'] = c2
                            rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"

                if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "05":
                    c2 = None
                    defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                    c2 = DEFECATION[defecation[0]]
                    if c2 != "05":
                        rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = None
                        rhs_record['group_oi8ts04']['C5'] = c2
                        if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] == "01":
                            if rhs_record['group_oi8ts04']['If_no_why']:
                                rhs_record['group_oi8ts04']['If_no_why'] = None

                        if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] == "02":
                            if not rhs_record['group_oi8ts04']['If_no_why']:
                                rhs_record['group_oi8ts04']['If_no_why'] = "08"
                    else:
                        flag = True
                        #print "03:" +str(record['group_ce0hf58/house_no'])
                        rhs_record['group_oi8ts04']['How_many_installments_have_you'] = None
                        rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "03"
                        rhs_record['group_oi8ts04']['Type_of_SBM_toilets'] = None
                        rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = None
                        rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                        rhs_record['group_oi8ts04']['If_no_why'] = None
                        rhs_record['group_oi8ts04']['If_yes_why'] = None

                        rhs_record['group_oi8ts04']['C2'] = c2
                        if 'group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_' in record  and record['group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_'] == "07":
                            c2 = "13"
                            rhs_record['group_oi8ts04']['C2'] = c2
                            rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"

            if not rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] :
                rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "02"
                rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = None
                rhs_record['group_oi8ts04']['How_many_installments_have_you'] = None
                c2 = None
                defecation = record['group_ye18c77/group_yw8pj39/Current_place_of_defecation_toilet'].split()
                c2 = DEFECATION[defecation[0]]
                if c2 == "05":
                    rhs_record['group_oi8ts04']['C2'] = c2
                    if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] in ["03","04", "05"]:
                        if 'group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_' in record and record['group_ye18c77/group_yw8pj39/where_the_individual_toilet_is_connected_to_'] == "07":
                            c2 = "13"
                            rhs_record['group_oi8ts04']['C2'] = c2
                            rhs_record['group_oi8ts04']['What_is_the_toilet_connected_to'] = "08"

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "02":
            rhs_record['group_oi8ts04']['Type_of_SBM_toilets'] = None
            if rhs_record['group_oi8ts04']['C2'] == "08":
                if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] == "01":
                    rhs_record['group_oi8ts04']['If_no_why'] = None
                if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] == "02":
                    rhs_record['group_oi8ts04']['If_yes_why'] = None

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01":
            if rhs_record['group_oi8ts04']['How_many_installments_have_you'] == "01":
                if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "05":
                    if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] == "02":
                        rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None
                        rhs_record['group_oi8ts04']['If_yes_why'] = None

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01":
            if rhs_record['group_oi8ts04']['How_many_installments_have_you'] in ["02","03"]:
                #print "Pre"
                if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "01":
                    #print "01"
                    rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                    rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None
                    rhs_record['group_oi8ts04']['If_yes_why'] = None
                    rhs_record['group_oi8ts04']['If_no_why'] = None

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01":
            if rhs_record['group_oi8ts04']['How_many_installments_have_you'] == "03":
                #print "-Pre"
                if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] in ["03","04"]:
                    #print "-03, 04"
                    rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                    rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None
                    rhs_record['group_oi8ts04']['If_yes_why'] = None
                    rhs_record['group_oi8ts04']['If_no_why'] = None

        if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "01":
            if rhs_record['group_oi8ts04']['How_many_installments_have_you'] == "03":
                if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "05":
                    rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] = "03"
                    rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] = None
                    rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = None
                    rhs_record['group_oi8ts04']['If_yes_why'] = None


        # if rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] == "02" and rhs_record['group_oi8ts04']['C2']=="05":
        #     if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv']:
        #         rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv']=None
        #     if rhs_record['group_oi8ts04']['If_no_why']:
        #         rhs_record['group_oi8ts04']['If_no_why'] = None

        if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv']=="02":
            if not rhs_record['group_oi8ts04']['If_no_why']:
                rhs_record['group_oi8ts04']['If_no_why'] = "08"

        if rhs_record['group_oi8ts04']['Are_you_interested_in_an_indiv'] == "01":
            rhs_record['group_oi8ts04']['What_kind_of_toilet_would_you_like'] = "02"

        org_curr =None
        if rhs_record['group_oi8ts04']['C1']:
            org_curr = rhs_record['group_oi8ts04']['C1']
        elif rhs_record['group_oi8ts04']['C2']:
            org_curr = rhs_record['group_oi8ts04']['C2']
        elif rhs_record['group_oi8ts04']['C3']:
            org_curr = rhs_record['group_oi8ts04']['C3']
        elif rhs_record['group_oi8ts04']['C4']:
            org_curr = rhs_record['group_oi8ts04']['C4']
        elif rhs_record['group_oi8ts04']['C5']:
            org_curr = rhs_record['group_oi8ts04']['C5']

        rhs_record['group_oi8ts04']['Current_place_of_defecation'] = org_curr
        # if rhs_record['group_oi8ts04']['When_did_you_receive_r_second_installment']:
        #     rhs_record['group_oi8ts04']['Have_you_applied_for_individua'] = "01"
        #     if rhs_record['group_oi8ts04']['Status_of_toilet_under_SBM'] == "01":
        #         rhs_record['group_oi8ts04']['C1'] = "01"
        #         rhs_record['group_oi8ts04']['Current_place_of_defecation'] = "01"

    flag=True
    return flag, rhs_record

def create_xml_string(xml_dict, repeat_dict, xml_root, xml_root_attr_id, xml_root_attr_version):
    xml_string = dicttoxml.dicttoxml(xml_dict, attr_type=False, custom_root=xml_root)
    # print(xml_string)
    # print("\n")
    root = ET.fromstring(xml_string)
    root.set('id', xml_root_attr_id)
    root.set('version', xml_root_attr_version)

    # repeat_dict = {'group_te3dx03' : { 'append_index' : 1, 'list' : toilet_info}}
    if repeat_dict:
        for key, val in repeat_dict.items():
            if val['list']:
                sub_ele = root.find(key)
                index = val['append_index']
                # create xml to be appened and append
                for sub_xml_dict in val['list']:
                    sub_xml_string = dicttoxml.dicttoxml(sub_xml_dict, attr_type=False, root=False)
                    # print('\n sub xml - %s -- '%index ,sub_xml_string)

                    sub_root = ET.fromstring(sub_xml_string)

                    sub_ele.insert(index, sub_root)
                    index = index + 1

    xml_string = ET.tostring(root, encoding="utf8", method='xml')
    # print('\n final xml -- ', xml_string)
    # write_log('created xml string to write')

    return root;

def create_xml_file(xml_root, filename, folderpath):
    file = filename + ".xml"
    xml_file = os.path.join(folderpath, file)

    directory = os.path.dirname(xml_file)

    if not os.path.exists(directory):
        os.makedirs(directory)

    xml_tree = ET.ElementTree(xml_root)

    xml_tree.write(xml_file, xml_declaration=True, encoding='utf-8', method="xml")

    # fp_read = open(xml_file, 'r')
    # soup = BeautifulSoup((fp_read.read().replace('\n','')), 'xml')
    # fp_read.close()
    # try:
    #     d = soup.prettify()
    #     #print soup.prettify()
    #     fp_write = open(xml_file, 'w')
    #     fp_write.write(d)
    #     fp_write.close()
    # except Exception as e:
    #     print "Error"
    #     print e
    #     print xml_file


    log_msg = "created xml file : " + xml_file
    # write_log(log_msg)
    # print(log_msg)

    return;