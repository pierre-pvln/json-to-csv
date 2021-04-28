#from IPython.core.display import display

import pandas as pd

def add_shipinfo(inputdf,reference_dir,reference_filename,verbose=False):
    '''
    Add ship info to dataset
    '''
    
    df_shipsdata = pd.read_excel(reference_dir+reference_filename,
                                 dtype=str,
                                 engine='openpyxl'
                                 )

    # drop any rows with empty mmsi value
    df_shipsdata = df_shipsdata.dropna(subset=['mmsi'])

#    df_shipsdata = df_shipsdata.fillna("")

    df_shipsdata['mmsi'] = df_shipsdata['mmsi'].astype(int)
    
    #add ships data to dataframe
    extdf = pd.merge(left=inputdf, right=df_shipsdata, how='left', left_on='mmsi', right_on='mmsi')

    extdf['mmsi'] = extdf['mmsi'].astype(str)
    extdf.drop(['naam'], axis=1, inplace=True)

    if verbose :
        print(extdf.head(5))
        print(extdf.tail(5))
    
    return extdf


import certifi
import urllib3
import json
import numpy as np

def add_shipinfo_v2(inputdf,reference_dir,reference_filename,verbose=False):
    '''
    Add ship info to dataset
    '''
    # use the default settings if filename is not given
    if reference_filename == "":
        if verbose: print("Using data from API function.")
            
        myHeaders = {}
        payload = {}

        for i, row in inputdf.iterrows():
            
            api_url='https://eepc9zb0rb.execute-api.eu-central-1.amazonaws.com/default/shipsinfo/'+str(inputdf.at[i,'mmsi'])
            http = urllib3.PoolManager(      #https://urllib3.readthedocs.io/en/latest/user-guide.html#ssl
                cert_reqs='CERT_REQUIRED',   #use certification verification
                ca_certs=certifi.where())    #with certifi
            req = http.request('GET', api_url, headers=myHeaders, fields=payload)
            data_file=json.loads(req.data.decode('utf-8'))
            print(data_file)

            if data_file['Count'] > 0: # mmsi with info found
                #      mmsi naam registratie-land eni tonnage tue soort-schip lengte breedte
                inputdf.at[i,'registratie-land'] = data_file['Items'][0]['country_of_registration']
                inputdf.at[i,'eni'] = data_file['Items'][0]['eni']
                inputdf.at[i,'tonnage'] = data_file['Items'][0]['tonnage']
                inputdf.at[i,'tue'] = data_file['Items'][0]['teu']
                inputdf.at[i,'soort-schip'] = data_file['Items'][0]['shiptype']
                inputdf.at[i,'lengte'] = data_file['Items'][0]['max_length_m']
                inputdf.at[i,'breedte'] = data_file['Items'][0]['max_width_m']

            if data_file['Count'] == 0: # mmsi with info not found
                #      mmsi naam registratie-land eni tonnage tue soort-schip lengte breedte
                inputdf.at[i,'registratie-land'] =  np.nan
                inputdf.at[i,'eni'] =  np.nan 
                inputdf.at[i,'tonnage'] =  np.nan
                inputdf.at[i,'tue'] =  np.nan
                inputdf.at[i,'soort-schip'] =  np.nan
                inputdf.at[i,'lengte'] =  np.nan
                inputdf.at[i,'breedte'] =  np.nan

    
        extdf=inputdf.copy()
            
    else:
        if verbose: print("Using default file as input.")    
        df_shipsdata = pd.read_excel(reference_dir+reference_filename,dtype=str)
        df_shipsdata = df_shipsdata.fillna("")
        df_shipsdata['mmsi'] = df_shipsdata['mmsi'].astype(int)

        #add ships data to dataframe
        extdf = pd.merge(left=inputdf, right=df_shipsdata, how='left', left_on='mmsi', right_on='mmsi')

        extdf['mmsi'] = extdf['mmsi'].astype(str)
        extdf.drop(['naam'], axis=1, inplace=True)

    if verbose :
        print(extdf.head(5))
        print(extdf.tail(5))
    
    return extdf
    

def missing_info(inputdf,check_column,verbose=False):
    
    if verbose: print(inputdf.columns)
    
    missing_ships = inputdf.loc[ inputdf[check_column].isnull(), ['mmsi','name']] 
    missing_ships.drop_duplicates(inplace=True)
    
    if verbose: print(missing_ships)
    
    
    return missing_ships


def countrystring(mmsi,strtype=0):
    '''
    mmsi = mmsi code of ship
    strtype = 0 name
              1 alpha-2
              2 alpha-3
    '''
    
    country_dict= {
         '201': ['Albania ','AL ','ALB '],
         '202': ['Andorra ','AD ','AND '],
         '203': ['Austria ','AT ','AUT '],
         '204': ['Azores ','PT ','PRT '],
         '205': ['Belgium ','BE ','BEL '],
         '206': ['Belarus ','BY ','BLR '],
         '207': ['Bulgaria ','BG ','BGR '],
         '208': ['Vatican City State ','VA ','VAT '],
         '209': ['Cyprus ','CY ','CYP '],
         '210': ['Cyprus ','CY ','CYP '],
         '211': ['Germany ','DE ','DEU '],
         '212': ['Cyprus ','CY ','CYP '],
         '213': ['Georgia ','GE ','GEO '],
         '214': ['Moldova ','MD ','MDA '],
         '215': ['Malta ','MT ','MLT '],
         '216': ['Armenia ','AM ','ARM '],
         '218': ['Germany ','DE ','DEU '],
         '219': ['Denmark ','DK ','DNK '],
         '220': ['Denmark ','DK ','DNK '],
         '224': ['Spain ','ES ','ESP '],
         '225': ['Spain ','ES ','ESP '],
         '226': ['France ','FR ','FRA '],
         '227': ['France ','FR ','FRA '],
         '228': ['France ','FR ','FRA '],
         '229': ['Malta ','MT ','MLT '],
         '230': ['Finland ','FI ','FIN '],
         '231': ['Faroe Islands ','FO ','FRO '],
         '232': ['United Kingdom ','GB ','GBR '],
         '233': ['United Kingdom ','GB ','GBR '],
         '234': ['United Kingdom ','GB ','GBR '],
         '235': ['United Kingdom ','GB ','GBR '],
         '236': ['Gibraltar ','GI ','GIB '],
         '237': ['Greece ','GR ','GRC '],
         '238': ['Croatia ','HR ','HRV '],
         '239': ['Greece ','GR ','GRC '],
         '240': ['Greece ','GR ','GRC '],
         '241': ['Greece ','GR ','GRC '],
         '242': ['Morocco ','MA ','MAR '],
         '243': ['Hungary ','HU ','HUN '],
         '244': ['Netherlands ','NL ','NLD '],
         '245': ['Netherlands ','NL ','NLD '],
         '246': ['Netherlands ','NL ','NLD '],
         '247': ['Italy ','IT ','ITA '],
         '248': ['Malta ','MT ','MLT '],
         '249': ['Malta ','MT ','MLT '],
         '250': ['Ireland ','IE ','IRL '],
         '251': ['Iceland ','IS ','ISL '],
         '252': ['Liechtenstein ','LI ','LIE '],
         '253': ['Luxembourg ','LU ','LUX '],
         '254': ['Monaco ','MC ','MCO '],
         '255': ['Madeira ','PT ','PRT '],
         '256': ['Malta ','MT ','MLT '],
         '257': ['Norway ','NO ','NOR '],
         '258': ['Norway ','NO ','NOR '],
         '259': ['Norway ','NO ','NOR '],
         '261': ['Poland ','PL ','POL '],
         '262': ['Montenegro ','ME ','MNE '],
         '263': ['Portugal ','PT ','PRT '],
         '264': ['Romania ','RO ','ROU '],
         '265': ['Sweden ','SE ','SWE '],
         '266': ['Sweden ','SE ','SWE '],
         '267': ['Slovak Republic ','SK ','SVK '],
         '268': ['San Marino ','SM ','SMR '],
         '269': ['Switzerland ','CH ','CHE '],
         '270': ['Czech Republic ','CZ ','CZE '],
         '271': ['Turkey ','TR ','TUR '],
         '272': ['Ukraine ','UA ','UKR '],
         '273': ['Russia ','RU ','RUS '],
         '274': ['Macedonia ','MK ','MKD '],
         '275': ['Latvia ','LV ','LVA '],
         '276': ['Estonia ','EE ','EST '],
         '277': ['Lithuania ','LT ','LTU '],
         '278': ['Slovenia ','SI ','SVN '],
         '279': ['Serbia ','RS ','SRB '],
         '301': ['Anguilla ','AI ','AIA '],
         '303': ['Alaska ','US ','USA '],
         '304': ['Antigua and Barbuda ','AG ','ATG '],
         '305': ['Antigua and Barbuda ','AG ','ATG '],
         '306': ['Antilles ','CW ','CUW '],
         '307': ['Aruba ','AW ','ABW '],
         '308': ['Bahamas ','BS ','BHS '],
         '309': ['Bahamas ','BS ','BHS '],
         '310': ['Bermuda ','BM ','BMU '],
         '311': ['Bahamas ','BS ','BMU '],
         '312': ['Belize ','BZ ','BLZ '],
         '314': ['Barbados ','BB ','BRB '],
         '316': ['Canada ','CA ','CAN '],
         '319': ['Cayman Islands ','KY ','CYM '],
         '321': ['Costa Rica ','CR ','CRI '],
         '323': ['Cuba ','CU ','CUB '],
         '325': ['Dominica ','DM ','DMA '],
         '327': ['Dominican Republic ','DO ','DOM '],
         '329': ['Guadeloupe ','GP ','GLP '],
         '330': ['Grenada ','GD ','GRD '],
         '331': ['Greenland ','GL ','GRL '],
         '332': ['Guatemala ','GT ','GTM '],
         '335': ['Honduras ','HN ','HND '],
         '336': ['Haiti ','HT ','HTI '],
         '338': ['United States of America ','US ','USA '],
         '339': ['Jamaica ','JM ','JAM '],
         '341': ['Saint Kitts and Nevis ','KN ','KNA '],
         '343': ['Saint Lucia ','LC ','LCA '],
         '345': ['Mexico ','MX ','MEX '],
         '347': ['Martinique ','MQ ','MTQ '],
         '348': ['Montserrat ','MS ','MSR '],
         '350': ['Nicaragua ','NI ','NIC '],
         '351': ['Panama ','PA ','PAN '],
         '352': ['Panama ','PA ','PAN '],
         '353': ['Panama ','PA ','PAN '],
         '354': ['Panama ','PA ','PAN '],
         '355': ['Panama ','PA ','PAN '],
         '356': ['Panama ','PA ','PAN '],
         '357': ['Panama ','PA ','PAN '],
         '358': ['Puerto Rico ','PR ','PRI '],
         '359': ['El Salvador ','SV ','SLV '],
         '361': ['Saint Pierre and Miquelon ','PM ','SPM '],
         '362': ['Trinidad and Tobago ','TT ','TTO '],
         '364': ['Turks and Caicos Islands ','TC ','TCA '],
         '366': ['United States of America ','US ','USA '],
         '367': ['United States of America ','US ','USA '],
         '368': ['United States of America ','US ','USA '],
         '369': ['United States of America ','US ','USA '],
         '370': ['Panama ','PA ','PAN '],
         '371': ['Panama ','PA ','PAN '],
         '372': ['Panama ','PA ','PAN '],
         '373': ['Panama ','PA ','PAN '],
         '374': ['Panama ','PA ','PAN '],
         '375': ['Saint Vincent and the Grenadines ','VC ','VCT '],
         '376': ['Saint Vincent and the Grenadines ','VC ','VCT '],
         '377': ['Saint Vincent and the Grenadines ','VC ','VCT '],
         '378': ['British Virgin Islands ','VG ','VGB '],
         '379': ['United States Virgin Islands ','VI ','VIR '],
         '401': ['Afghanistan ','AF ','AFG '],
         '403': ['Saudi Arabia ','SA ','SAU '],
         '405': ['Bangladesh ','BD ','BGD '],
         '408': ['Bahrain ','BH ','BHR '],
         '410': ['Bhutan ','BT ','BTN '],
         '412': ['China ','CN ','CHN '],
         '413': ['China ','CN ','CHN '],
         '414': ['China ','CN ','CHN '],
         '416': ['Taiwan ','TW ','TWN '],
         '417': ['Sri Lanka ','LK ','LKA '],
         '419': ['India ','IN ','IND '],
         '422': ['Iran ','IR ','IRN '],
         '423': ['Azerbaijan ','AZ ','AZE '],
         '425': ['Iraq ','IQ ','IRQ '],
         '428': ['Israel ','IL ','ISR '],
         '431': ['Japan ','JP ','JPN '],
         '432': ['Japan ','JP ','JPN '],
         '434': ['Turkmenistan ','TM ','TKM '],
         '436': ['Kazakhstan ','KZ ','KAZ '],
         '437': ['Uzbekistan ','UZ ','UZB '],
         '438': ['Jordan ','JO ','JOR '],
         '440': ['Korea ','KR ','KOR '],
         '441': ['Korea ','KR ','KOR '],
         '443': ['State of Palestine ','PS ','PSE '],
         '445': ['Democratic Peoples Republic of Korea ','KP ','PRK '],
         '447': ['Kuwait ','KW ','KWT '],
         '450': ['Lebanon ','LB ','LBN '],
         '451': ['Kyrgyz Republic ','KG ','KGZ '],
         '453': ['Macao ','MO ','MAC '],
         '455': ['Maldives ','MV ','MDV '],
         '457': ['Mongolia ','MN ','MNG '],
         '459': ['Nepal ','NP ','NPL '],
         '461': ['Oman ','OM ','OMN '],
         '463': ['Pakistan ','PK ','PAK '],
         '466': ['Qatar (State of) ','QA ','QAT '],
         '468': ['Syrian Arab Republic ','SY ','SYR '],
         '470': ['United Arab Emirates ','AE ','ARE '],
         '472': ['Tajikistan ','TJ ','TJK '],
         '473': ['Yemen ','YE ','YEM '],
         '475': ['Yemen ','YE ','YEM '],
         '477': ['Hong Kong ','HK ','HKG '],
         '478': ['Bosnia and Herzegovina ','BA ','BIH '],
         '501': ['Adelie Land ','FR ','FRA '],
         '503': ['Australia ','AU ','AUS '],
         '506': ['Myanmar ','MM ','MMR '],
         '508': ['Brunei Darussalam ','BN ','BRN '],
         '510': ['Micronesia ','FM ','FSM '],
         '511': ['Palau ','PW ','PLW '],
         '512': ['New Zealand ','NZ ','NZL '],
         '514': ['Cambodia ','KH ','KHM '],
         '515': ['Cambodia ','KH ','KHM '],
         '516': ['Christmas Island ','CX ','CXR '],
         '518': ['Cook Islands ','CK ','COK '],
         '520': ['Fiji ','FJ ','FJI '],
         '523': ['Cocos (Keeling) Islands ','CC ','CCK '],
         '525': ['Indonesia ','ID ','IDN '],
         '529': ['Kiribati ','KI ','KIR '],
         '531': ['Lao Peoples Democratic Republic ','LA ','LAO '],
         '533': ['Malaysia ','MY ','MYS '],
         '536': ['Northern Mariana Islands ','MP ','MNP '],
         '538': ['Marshall Islands ','MH ','MHL '],
         '540': ['New Caledonia ','NC ','NCL '],
         '542': ['Niue ','NU ','NIU '],
         '544': ['Nauru ','NR ','NRU '],
         '546': ['French Polynesia ','PF ','PYF '],
         '548': ['Philippines ','PH ','PHL '],
         '553': ['Papua New Guinea ','PG ','PNG '],
         '555': ['Pitcairn Island ','PN ','PCN '],
         '557': ['Solomon Islands ','SB ','SLB '],
         '559': ['American Samoa ','AS ','ASM '],
         '561': ['Samoa ','WS ','WSM '],
         '563': ['Singapore ','SG ','SGP '],
         '564': ['Singapore ','SG ','SGP '],
         '565': ['Singapore ','SG ','SGP '],
         '566': ['Singapore ','SG ','SGP '],
         '567': ['Thailand ','TH ','THA '],
         '570': ['Tonga ','TO ','TON '],
         '572': ['Tuvalu ','TV ','TUV '],
         '574': ['Viet Nam ','VN ','VNM '],
         '576': ['Vanuatu ','VU ','VUT '],
         '577': ['Vanuatu ','VU ','VUT '],
         '578': ['Wallis and Futuna Islands ','WF ','WLF '],
         '601': ['South Africa ','ZA ','ZAF '],
         '603': ['Angola ','AO ','AGO '],
         '605': ['Algeria ','DZ ','DZA '],
         '607': ['Saint Paul and Amsterdam Islands ','FR ','FRA '],
         '608': ['Ascension Island ','GB ','GBR '],
         '609': ['Burundi ','BI ','BDI '],
         '610': ['Benin ','BJ ','BEN '],
         '611': ['Botswana ','BW ','BWA '],
         '612': ['Central African Republic ','CF ','CAF '],
         '613': ['Cameroon ','CM ','CMR '],
         '615': ['Congo ','CG ','COG '],
         '616': ['Comoros ','KM ','COM '],
         '617': ['Cabo Verde ','CV ','CPV '],
         '618': ['Crozet Archipelago ','FR ','FRA '],
         '619': ['Ivory Coast ','CI ','CIV '],
         '620': ['Comoros ','KM ','COM '],
         '621': ['Djibouti ','DJ ','DJI '],
         '622': ['Egypt ','EG ','EGY '],
         '624': ['Ethiopia ','ET ','ETH '],
         '625': ['Eritrea ','ER ','ERI '],
         '626': ['Gabonese Republic ','GA ','GAB '],
         '627': ['Ghana ','GH ','GHA '],
         '629': ['Gambia ','GM ','GMB '],
         '630': ['Guinea-Bissau ','GW ','GNB '],
         '631': ['Equatorial Guinea ','GQ ','GNQ '],
         '632': ['Guinea ','GN ','GIN '],
         '633': ['Burkina Faso ','BF ','BFA '],
         '634': ['Kenya ','KE ','KEN '],
         '635': ['Kerguelen Islands ','FR ','FRA '],
         '636': ['Liberia ','LR ','LBR '],
         '637': ['Liberia ','LR ','LBR '],
         '638': ['South Sudan ','SS ','SSD '],
         '642': ['Libya ','LY ','LBY '],
         '644': ['Lesotho ','LS ','LSO '],
         '645': ['Mauritius ','MU ','MUS '],
         '647': ['Madagascar ','MG ','MDG '],
         '649': ['Mali ','ML ','MLI '],
         '650': ['Mozambique ','MZ ','MOZ '],
         '654': ['Mauritania ','MR ','MRT '],
         '655': ['Malawi ','MW ','MWI '],
         '656': ['Niger ','NE ','NER '],
         '657': ['Nigeria ','NG ','NGA '],
         '659': ['Namibia ','NA ','NAM '],
         '660': ['Reunion ','RE ','REU '],
         '661': ['Rwanda ','RW ','RWA '],
         '662': ['Sudan ','SD ','SDN '],
         '663': ['Senegal ','SN ','SEN '],
         '664': ['Seychelles ','SC ','SYC '],
         '665': ['Saint Helena ','SH ','SHN '],
         '666': ['Somali Democratic Republic ','SO ','SOM '],
         '667': ['Sierra Leone ','SL ','SLE '],
         '668': ['Sao Tome and Principe ','ST ','STP '],
         '669': ['Swaziland ','SZ ','SWZ '],
         '670': ['Chad ','TD ','TCD '],
         '671': ['Togolese Republic ','TG ','TGO '],
         '672': ['Tunisian Republic ','TN ','TUN '],
         '674': ['Tanzania ','TZ ','TZA '],
         '675': ['Uganda ','UG ','UGA '],
         '676': ['Democratic Republic of the Congo ','CD ','COD '],
         '677': ['Tanzania ','TZ ','TZA '],
         '678': ['Zambia ','ZM ','ZMB '],
         '679': ['Zimbabwe ','ZW ','ZWE '],
         '701': ['Argentine Republic ','AR ','ARG '],
         '710': ['Brazil ','BR ','BRA '],
         '720': ['Bolivia ','BO ','BOL '],
         '725': ['Chile ','CL ','CHL '],
         '730': ['Colombia ','CO ','COL '],
         '735': ['Ecuador ','EC ','ECU '],
         '740': ['Falkland Islands ','FK ','FLK '],
         '745': ['Guiana ','GF ','GUF '],
         '750': ['Guyana ','GY ','GUY '],
         '755': ['Paraguay ','PY ','PRY '],
         '760': ['Peru ','PE ','PER '],
         '765': ['Suriname ','SR ','SUR '],
         '770': ['Uruguay ','UY ','URY '],
         '775': ['Venezuela ','VE ','VEN ']
    }
    
    return country_dict[str(mmsi)[0:3]][strtype]