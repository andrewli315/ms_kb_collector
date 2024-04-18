import requests
import sqlite3
from datetime import datetime
from product import *
#curl -X GET --header 'Accept: application/json' 'https://api.msrc.microsoft.com/cvrf/v3.0/cvrf/2024-Feb' 

api_url = "https://api.msrc.microsoft.com/cvrf/v3.0/cvrf/"

month = ['Jan', 'Feb', 'Mar', 'Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def parse(year, month):
    url = api_url + "{}-{}".format(year, month)
    print(url)
    headers = {
            "Accept":"application/json"
            }

    try:
        res = requests.get(url, headers=headers)
        return res.json()
    except Exception as e : 
        print(e)
        return 1

def parse_with_month(year, month_index):

    parse_result = parse(year, month[month_index])
    print(parse_result)
#    items = parse_result["ProductTree"]["Branch"]
#    print(items)
#    vulns = parse_result['Vulnerability']
#    print(vulns[0]["Remediations"])
        
def to_database(year, n_month):
    session = create_local_engine()


    for i in range(n_month):            
        parse_result = parse(year, month[i])
        if parse_result == "Unable to find the specified file.":
            continue
        items = parse_result["ProductTree"]["Branch"][0]["Items"]

        productID_mapping = {}       
        products = [] 
        for item in items:
            if item["Name"] == "Microsoft":
                for ms in item["Items"]:
                    for product in ms["Items"]:
                        ret = session.query(Product).filter_by( productID = product['ProductID']).first()
                        if ret is None:
                               
                            prod = Product(product['ProductID'], product['Value'])  
                            products.append(prod)

                        productID_mapping[product['ProductID']] = product['Value']

            else:
                for other in item["Items"]:
                    ret = session.query(Product).filter_by(productID = other['ProductID']).first()
                    if ret is None:
                        prod = Product(other['ProductID'], other['Value'])  
                        products.append(prod)
                    productID_mapping[other["ProductID"]] = other["Value"]
            

        session.add_all(products)
        session.commit()
        vulns = parse_result['Vulnerability']
        if vulns is not None:
            for vuln in vulns:
                try:
                    date = datetime.fromisoformat(vuln["RevisionHistory"][len(vuln["RevisionHistory"]) - 1]["Date"])
                except:
                    date = datetime.strptime(vuln["RevisionHistory"][len(vuln["RevisionHistory"]) - 1]["Date"], '%Y-%m-%dT%H:%M:%SZ')
                if type(vuln) is list:
                    vuln = vuln[0]

                for rem in vuln["Remediations"]:                
                    if "Value" not in rem["Description"]:
                        continue
                    if rem['Description']['Value'].isnumeric():
                        kb_num = "KB"+"{}".format(rem['Description']['Value'])
                        kb_ret = session.query(KB_Number).filter_by(patch_number = kb_num).first()
                        if kb_ret is None:
                            kb = KB_Number(kb_num, date)
                            affected_products = []
                            for prod in rem['ProductID']:
                                affected_product  = session.query(Product).filter_by(productID = prod).first()
                                affected_products.append(affected_product)
                            kb.add_affected_product(affected_products)
                            session.add(kb)
            session.commit()

if __name__ == "__main__":
    year = 2016
    n_month = 12
    to_database(year, n_month)
    #parse_with_month(2016, 1)


