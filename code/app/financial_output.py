#from IPython.core.display import display

import pandas as pd


def add_billing_info(inputdf, reference_dir, reference_filename, verbose=False):
    '''
    Add billing info to dataset
    '''
    
    columnslist = list(inputdf.columns.values)
    print(columnslist)
    # print(inputdf.dtypes)
    # print(inputdf)

    inputdf['mmsi'] = inputdf['mmsi'].astype(int)
    # inputdf['mmsi'] = inputdf['mmsi'].apply(np.int64)
    # ##inputdf['mmsi'] = pd.to_numeric(inputdf['mmsi'],errors='coerce')
    # ##might need to change nan input to 0
    # ##https://datatofish.com/string-to-integer-dataframe/
    
    # df_billing_info = pd.read_excel(reference_dir+reference_filename,dtype=str)
    df_billing_info = pd.read_excel(reference_dir+reference_filename,
                                    dtype=str,
                                    engine='openpyxl'
                                    )
    
    df_billing_info = df_billing_info.fillna("")
    
    # remove eni column if it exists
    if 'eni' in df_billing_info.columns:
        df_billing_info = df_billing_info.drop(['eni'], axis=1)
    
    print(df_billing_info)

    # drop any rows with empty/nan mmsi value
    df_billing_info = df_billing_info.dropna(subset=['mmsi'])
    df_billing_info = df_billing_info[df_billing_info.mmsi != ""]

    df_billing_info['mmsi'] = df_billing_info['mmsi'].astype(int)
    
    # add specific billing info for geozone (if defined)
    detaildf = pd.merge(left=inputdf, right=df_billing_info,
                        how='left', 
                        left_on=['mmsi', 'location_zone'], right_on=['mmsi', 'geozone'])
    
    # Those that are not found get NaN value and replace that with ""    
    detaildf = detaildf.fillna("")
    print(detaildf.columns)
    print(detaildf)
    print("======================")
    
    genericdf = detaildf[detaildf['factuur naam'] == ""].copy()
    print(genericdf.columns)
    print(genericdf)
    print("----------------------")
    
    # remove columns added in merge
    
    genericdf.drop(columns=[col for col in genericdf if col not in columnslist], inplace=True)
    
    print(genericdf.columns)
    print(genericdf)   
    print("++++++++++++++++++++++")
     
    print(detaildf['factuur naam'])
        
    # detaildf.drop( detaildf['factuur naam']=="",inplace=True)

    detaildf.drop(detaildf.index[detaildf['factuur naam'] == ""], inplace=True)

    print(detaildf.columns)
    print(detaildf)
    print("//////////////////////")
    
    extdf = pd.merge(left=genericdf, right=df_billing_info,
                     how='left', 
                     left_on=['mmsi'], right_on=['mmsi'])

#    detaildf=detaildf.fillna("")
        
#    print(detaildf[[ 'name', 'geozone','factuur naam']])

#    print("+++++++++++++++++++++++++++++++++")

    # select the rows that have no billing address
#    genericdf= detaildf[ detaildf['geozone']!= "" ]
    # and drop the billing info columns

#    extdf = pd.merge(left=genericdf, right=df_billing_info,
#                     how='left', left_on=['mmsi'], right_on=['mmsi'])
    
    extdf = extdf.append(detaildf, ignore_index=True)
    print(extdf.columns)
    print(extdf)
    print("llllllllllllllllllllll")
        
    # default_billing_info=df_billing_info[df_billing_info['geozone']==""]
    # print(default_billing_info)
    
    # add billing data to dataframe
    # extdf = pd.merge(left=inputdf, right=default_billing_info, how='left', left_on='mmsi', right_on='mmsi')
     
    # detailed_billing_info=df_billing_info[df_billing_info['geozone']!=""]
    # print(detailed_billing_info)
    
    # add billing data to dataframe
    # extdf = pd.merge(left=inputdf, right=detailed_billing_info, how='left', left_on='mmsi', right_on='mmsi')
        
    # extdf['callsign_count'] = extdf['callsign_count'].astype(str)
    # extdf['mmsi'] = extdf['mmsi'].astype(str)
    # extdf.drop(['naam'], axis=1, inplace=True)
    
    # if verbose :
    #    print(extdf.head(5))
    #    print(extdf.tail(5))
    
    return extdf
