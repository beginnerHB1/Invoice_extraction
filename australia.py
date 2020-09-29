import re
import pdftotext

#australia
def create_json(lst_det):
    if "DATE" in lst_det[0]:
        final_2 = "mmddyyyy"
        final_1 = lst_det[-1]

    elif type(lst_det[-1]) == list:
        final_2 = len("-".join(lst_det[-1]))
        final_1 = "-".join(lst_det[-1])

    else:
        final_2 = len(lst_det[-1].strip())
        final_1 = lst_det[-1].strip()
    return {"Field Name":lst_det[0],
            "length": final_2,
            "Mandotory":lst_det[1],
            "Sample Value":final_1}

def find_regex(text):
    dct = {}
    pattern_dct = {
                    "abn" : "[0-9]{2} [0-9]{3} [0-9]{3} [0-9]{3}",
                    "date" : "[0-9]{1,2}[\/]{1}[0-9]{2}[\/]{1}[0-9]{4}",
                    "phone_fax" : "[0-9]{2} [0-9]{4} [0-9]{4}",
                    # "invoice_num" : "[A-Z][0-9]{7}",
                    "case_number" : " [0-9]{8}\n"
                    }

    for i in list(pattern_dct.keys()):
        # try:
        dct[i] =  re.findall(pattern_dct[i], text)
        # except:
        #     dct[i] =  ""
    dct["phone"] = dct["phone_fax"][0]
    dct["fax"] = dct["phone_fax"][1]
    del dct["phone_fax"]

    for i in text.split("\n"):
        if "TAX INVOICE" in i:
            invoice_num = i.split("TAX INVOICE")[-1].strip()
            break
        elif "COMMERCIAL INVOICE" in i:
            invoice_num = i.split("COMMERCIAL INVOICE")[-1].strip()
            break
    dct["invoice_num"] = invoice_num

    return dct

def find_table_details(text):
    try:
        end_index, start_index = text.index("CASE TOTAL"), text.index("SUPPLIED")+8
        table_data = text[start_index:end_index].strip().split("\n")
        # print(table_data)
        if len(table_data) >= 2:
            for i,j in enumerate(table_data):
                try:
                    re_pattern = "[1-9]{1,2} [A-Z]{4} "
                    tx = re.findall(re_pattern, "".join(j))[0]
                    start = table_data[i].index(tx)
                    end = start + 6
                    table_data[i] = "".join(table_data[i][:start]) + "-".join(table_data[i][start:end].split()) + "".join(table_data[i][end:])
                except IndexError:
                    pass
            details_table = []
            lst = []
            for i in table_data:
                if len(i.split()) != 0 and "--------" not in i:
                    lst.append(i.split())

            for i in range(len(lst)):
                for j, k in enumerate(lst[i]):
                    if len(k) < 2:
                        lst[i].remove(lst[i][j])
                    else:
                        pass
            k = 0
            # print(lst)
            for i,j in enumerate(lst):
                if "---------------" not in j:
                    if len(j) >= 7:
                        details_table.append(create_json([f"PART NUMBER_{k}", "yes", j[0]]))
                        details_table.append(create_json([f"DO NUMBER_{k}", "yes", j[1]]))
                        details_table.append(create_json([f"HARMONISED_{k}", "yes", j[2]]))
                        details_table.append(create_json([f"COUNTRY_{k}", "yes", " ".join(j[3:-3])]))
                        details_table.append(create_json([f"QUANTITY UNIT_{k}", "yes",j[-3]]))
                        details_table.append(create_json([f"UNIT VALUE_{k}", "yes", j[-2]]))
                        details_table.append(create_json([f"AMOUNT_{k}", "yes", j[-1]]))

                        if len(lst[i+1]) == 2:
                            details_table.append(create_json([f"Description_{k}", "yes", lst[i+1][0]]))
                            details_table.append(create_json([f"cus_ord_{k}", "yes", lst[i+1][1]]))
                            k += 1
                        elif len(lst[i+1]) == 3:
                            details_table.append(create_json([f"Description_{k}", "yes", " ".join(lst[i+1][0:2])]))
                            details_table.append(create_json([f"cus_ord_{k}", "yes",lst[i+1][2]]))
                            k += 1
                    # elif len(j) == 2:
                        # details_table.append(create_json([f"Description_{k}", "yes", j[0]]))
                        # details_table.append(create_json([f"cus_ord_{k}", "yes", j[1]]))
                    # elif len(j) == 3:
                        # details_table.append(create_json([f"Description_{k}", "yes", " ".join(j[0:2])]))
                        # details_table.append(create_json([f"cus_ord_{k}", "yes", j[2]]))
                        
            return details_table
        else:
            False
    except:
        False

def find_details_australia(pdf):
    json_dct = {"Header":[],
                "Delivered To":[],
                "Mail To":[],
                "Line Details (Repeated Segment)":[],
                "Invoice Amount Details":[]}

    with open(pdf, "rb") as f:
        pdf = pdftotext.PDF(f)

    data = " "
    for i in range(len(pdf)):
        data += "\n" +  pdf[i]

    # try:
    dct = find_regex(data)
    for i in list(dct.keys()):
        json_dct["Header"].append(create_json([i,"yes",
                                                    dct[i]]
                                                    ))
        
    cus_no = data[data.index("CUSTOMER NO"): data.index("DELIVERED TO")]
    if "ABN" in cus_no:
        final_cus_no = cus_no.split("ABN")[0]
    else:
        final_cus_no = cus_no.split(":")[-1].strip()

    json_dct["Header"].append(create_json(["customer_no","yes",
                                        final_cus_no]
                                        ))

    # except:
    #     json_dct["Header"] = []

    try:
        table = find_table_details(data)
        json_dct["Line Details (Repeated Segment)"] = table
    except:
        json_dct["Line Details (Repeated Segment)"] = []

    x = data.split("\n")
    # headers
    for i in range(len(x)):
        if "CASE NUMBER" in x[i]:
            x[i] = x[i][:x[i].index("CASE NUMBER")]

        elif "PAGE" in x[i]:
            x[i] = x[i][:x[i].index("PAGE")]


        elif "SUPP. CASE NO" in x[i]:
            x[i] = x[i][:x[i].index("SUPP. CASE NO")]

        elif "DATE INV/DEL" in x[i]:
            x[i] = x[i][:x[i].index("DATE INV/DEL")]

        elif "INVOICE CURRENCY" in x[i]:
            try:
                json_dct["Header"].append(create_json(["INVOICE_CURRENCY","yes",
                                            x[i].strip().split(":")[-1]]
                                            ))
                x[i] = x[i][:x[i].index("INVOICE")]
            # print(x[i])
            except:
                continue


        elif "CASE TOTAL" in x[i]:
            try:
                json_dct["Invoice Amount Details"].append(create_json(["Case_total","yes",
                                            x[i].strip().split(":")[-1]]
                                            ))
            except:
                continue

        elif "GST @10%" in x[i]:
            try:
                json_dct["Invoice Amount Details"].append(create_json(["GST @10%","yes",
                                            x[i].strip().split(":")[-1]]
                                            ))
            except:
                continue

        elif "INVOICE TOTAL" in x[i]:
            try:
                json_dct["Invoice Amount Details"].append(create_json(["INVOICE TOTAL","yes",
                                            x[i].strip().split(":")[-1]]
                                            ))
            except:
                continue

    for i in range(len(x)):
        if "DELIVERED TO" in x[i]:
            x[i] = x[i].strip()
            deliver_start_index = x.index(x[i])
            x[i] = x[i][x[i].index(":")+1:]

        elif "MAIL TO :" in x[i]:
            x[i] = x[i].strip()
            deliver_end_index = x.index(x[i])
            receiver_start_index = x.index(x[i])
            x[i] = x[i][x[i].index(":")+1:]

        elif "------" in x[i]:
            x[i] = x[i].strip()
            receiver_end_index = x.index(x[i])
            table_start_index = x.index(x[i])
    try:
        lst = [i.strip() for i in x[deliver_start_index:deliver_end_index]]
        json_dct["Delivered To"].append(create_json(["Delivered To","yes",
                                " ".join(lst)]
                                ))
        lst = [i.strip() for i in x[receiver_start_index: receiver_end_index]]
        json_dct["Mail To"].append(create_json(["MAIL To","yes",
                                " ".join(lst)]
                                ))
    except:
        pass

    return json_dct
