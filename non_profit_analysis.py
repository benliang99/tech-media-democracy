import requests
import pandas as pd

extracted_data_path = 'extracted_data/'
google_political_ads_file_path = 'raw_data_sources/google-political-ads-advertiser-stats.csv'

def load_data(raw_data_path, extracted_data_path):
    """Load the data from CSV and filter for non-profit advertisers."""
    data = pd.read_csv(raw_data_path)
    data_us = data[data['Regions'].str.contains('US', na=False)]
    ein_data = data_us[data_us['Public_IDs_List'].str.contains('EIN', na=False)]
    ein_data.to_csv(extracted_data_path + 'advertisers_ein_us.csv', index=False)
    fec_data = data_us[data_us['Public_IDs_List'].str.contains('FEC', na=False)]
    fec_data.to_csv(extracted_data_path + 'advertisers_fec_us.csv', index=False)
    return ein_data, fec_data

# https://projects.propublica.org/nonprofits/api
def validate_ein(ein_list):
    """Validate EINs using ProPublica's Nonprofit API and store details of valid and invalid EINs."""
    base_url = "https://projects.propublica.org/nonprofits/api/v2/organizations/"
    valid_eins = []
    invalid_eins = []
    for ein in ein_list:
        url = f"{base_url}{ein}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            org = data.get('organization')
            if org:
                print(f"Valid EIN: {org['ein']} | Name: {org['name']} | Address: {org['address']}, {org['city']}, {org['state']}, {org['zipcode']}")
                valid_eins.append(ein)
            else:
                print(f"Invalid EIN: {ein} - No organization data found.")
                invalid_eins.append(ein)
        else:
            print(f"Invalid EIN: {ein} - Failed to retrieve data with status code: {response.status_code}")
            invalid_eins.append(ein)
    return valid_eins, invalid_eins

def main():
    ein_data, fec_data = load_data(google_political_ads_file_path, extracted_data_path)
    ein_numbers = ein_data['Public_IDs_List'].str.extract('EIN ID (\d+-?\d*)')[0].dropna().unique()
    valid_ein_numbers, invalid_ein_numbers = validate_ein(ein_numbers)
    print(f"Number of valid EINs: {len(valid_ein_numbers)}")
    print(f"Number of invalid EINs: {len(invalid_ein_numbers)}")
    pd.Series(valid_ein_numbers).to_csv('valid_eins.csv', index=False)
    pd.Series(invalid_ein_numbers).to_csv('invalid_eins.csv', index=False)

if __name__ == '__main__':
    main()  
    