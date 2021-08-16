import os
import requests
import pandas as pd

BASE_URL = "https://rxnav.nlm.nih.gov"

#Regimen = "Cytotoxic"
#Regimen = "Targeted"
#Regimen = "Immunotherapy"
Regimen = "Endocrine"

def query_class():
    return

def clinical_concepts_list(df, col):
    lst = "; ".join(list(df[col].astype(str).drop_duplicates()))
    return lst

def query_brand_name_rxnorm_id(brand_name, testDrugs):
    search_brand_name = brand_name.replace(" ", "+")
    data = requests.get(f"{BASE_URL}/REST/rxcui.json?name={search_brand_name}").json()
    try:
        rxnorm_id = data["idGroup"]["rxnormId"][0]
        testDrugs.append(brand_name)
    except KeyError:
        testDrugs = pd.DataFrame({"Drugs": testDrugs})
        testDrugs.to_csv("testedDrugs.csv", mode='a', header=not os.path.exists("testedDrugs.csv"))
        
        print (data)
        exit()
    return rxnorm_id

def query_branded_dose_form_group_rxnorm_id(rxnorm_id):
    print (rxnorm_id)
    data = requests.get(f"{BASE_URL}/REST/rxcui/{rxnorm_id}/allrelated.json?").json()
    SBDG = [i for i in data["allRelatedGroup"]["conceptGroup"] if i["tty"]=="SBDG"][0]["conceptProperties"]
    if len(SBDG) == 1:
        return SBDG[0]["rxcui"]
    elif len(SBDG) == 0:
        return None
    else:
        rxcui_lst = [i["rxcui"] for i in SBDG]
        return "+".join(rxcui_lst)


def query_branded_dose_form_group_name(rxnorm_id):
    data = requests.get(f"{BASE_URL}/REST/rxcui/{rxnorm_id}/allrelated.json?").json()
    SBDG = [i for i in data["allRelatedGroup"]["conceptGroup"] if i["tty"]=="SBDG"][0]["conceptProperties"]

    if len(SBDG) == 1:
        return SBDG[0]["rxcui"]
    elif len(SBDG) == 0:
        return None
    else:
        rxcui_lst = [i["name"] for i in SBDG]
        return "+".join(rxcui_lst)


def query_by_type(branded_drugs, type, testDrugs):

    output = pd.DataFrame({
        "Branded Drug": [],
        "Clinical Drug Name": [],
        "Concept ID": [],
        "Type": []
    })
    currentTestedDrugs = []
    
    for branded_drug in branded_drugs:
        print (branded_drug)
        rxnorm_id = query_brand_name_rxnorm_id(branded_drug, currentTestedDrugs)
        
        data = requests.get(f"{BASE_URL}/REST/rxcui/{rxnorm_id}/allrelated.json?").json()
        print(f"{BASE_URL}/REST/rxcui/{rxnorm_id}/allrelated.json?")
        
        for t in type:
            temp_output = {}
            type_rxnorm_id = []
            type_concept_name = []
            
            try:
                concepts = [i for i in data["allRelatedGroup"]["conceptGroup"] if i["tty"]==f"{t}"][0]["conceptProperties"]
                concepts_present = True
            except KeyError:
                concepts_present = False

            if concepts_present:
                if len(concepts) == 1:
                    type_rxnorm_id.append(concepts[0]["rxcui"])
                    type_concept_name.append(concepts[0]["name"])

                elif len(concepts) == 0:
                    type_rxnorm_id.append(None)
                    type_concept_name.append(None)

                else:
                    type_rxnorm_id += [i["rxcui"] for i in concepts]
                    type_concept_name += [i["name"] for i in concepts]

                temp_output["Branded Drug"] = [branded_drug for i in range(len(type_rxnorm_id))]
                temp_output["Clinical Drug Name"] = type_concept_name
                temp_output["Concept ID"] = type_rxnorm_id
                temp_output["Type"] = [t for i in range(len(type_rxnorm_id))]
                temp_output = pd.DataFrame(temp_output)
                
                output = pd.concat([output, temp_output])
    
    return output

if os.path.isfile("testedDrugs.csv"):
    testDrugs = set(list(pd.read_csv("testedDrugs.csv")["Drugs"]))
else:
    testDrugs = []

if not os.path.isfile(f"Concept_set_{Regimen}_Therapies.csv") or False:
    cytotoxic = pd.read_csv(f"{Regimen} Therapies.csv")
    #drugs = [i for i in list(cytotoxic["Therapies"]) if i not in testDrugs]
    drugs = list(cytotoxic["Therapies"])
    print (drugs)

    clinical_drugs = query_by_type(branded_drugs=drugs, type=["SBDC", "SCDC", "SCD", "GPCK", "SBD", "BPCK", "IN", "MIN"], testDrugs=drugs)
    clinical_drugs = clinical_drugs.drop_duplicates()
    print (clinical_drugs)
    clinical_drugs.to_csv(f"Concept_set_{Regimen}_Therapies.csv", index=False)

    clinical_con_lst = clinical_concepts_list(clinical_drugs, col="Concept ID")
    print (clinical_con_lst)
else:
    clinical_drugs = pd.read_csv(f"Concept_set_{Regimen}_Therapies.csv")
    clinical_con_list = clinical_concepts_list(clinical_drugs, col="Concept ID")
    print (clinical_con_list)
