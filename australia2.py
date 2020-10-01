import pdftotext
import re

def find_regex(text):
    dct = {}
    for i in text.split("\n"):
        if "TAX INVOICE" in i:
            invoice_num = i.split("TAX INVOICE")[-1].strip()
            break
        elif "COMMERCIAL INVOICE" in i:
            invoice_num = i.split("COMMERCIAL INVOICE")[-1].strip()
            break
    dct["invoice_num"] = invoice_num
    dct["abn"] = re.findall("[0-9]{2} [0-9]{3} [0-9]{3} [0-9]{3}", text)[0].strip()
    dct["date"] = re.findall("[0-9]{1,2}[\/]{1}[0-9]{2}[\/]{1}[0-9]{4}", text)[0].strip()
    dct["phone"] = re.findall("[0-9]{2} [0-9]{4} [0-9]{4}", text)[0].strip()
    dct["fax"] = re.findall("[0-9]{2} [0-9]{4} [0-9]{4}", text)[1].strip()
    dct["case_number"] = re.findall(" [0-9]{8}\n", text)[0].strip()
    return dct

#done
def find_table_details(text):
    try:
        lst_line_det = []
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

            for i,j in enumerate(lst):
                if "---------------" not in j:
                    
                    if len(j) >= 7:
                        dct_line = {}
                        dct_line["partnumber"] = j[0].strip()
                        dct_line["donumber"] = j[1].strip()
                        dct_line["harmonised"] = j[2].strip()
                        dct_line["country"] = " ".join(j[3:-3]).strip()
                        dct_line["quantityunit"] = j[-3].strip()
                        dct_line["unitvalue"] = j[-2].strip()
                        dct_line["amount"] = j[-1].strip()


                        if len(lst[i+1]) == 2:
                            dct_line["description"] = lst[i+1][0].strip()
                            dct_line["cus_ord"] = lst[i+1][1].strip()
                            
                        elif len(lst[i+1]) == 3:
                            dct_line["description"] = " ".join(lst[i+1][0:2]).strip()
                            dct_line["cus_ord"] = lst[i+1][2].strip()

                        lst_line_det.append(dct_line)
            return lst_line_det
        else:
            False
    except:
        False

def find_details_australia(pdf):
    json_dct = {"supplier":"australia",
                "LineDetails":[],
                "InvoiceAmountDetails":[]}
    
    invoice_am = {}

    with open(pdf, "rb") as f:
        pdf = pdftotext.PDF(f)

    data = " "
    for i in range(len(pdf)):
        data += "\n" +  pdf[i]


    dct = find_regex(data)

    cus_no = data[data.index("CUSTOMER NO"): data.index("DELIVERED TO")]

    if "ABN" in cus_no:
        final_cus_no = cus_no.split("ABN")[0]
    else:
        final_cus_no = cus_no.split(":")[-1].strip()
    dct["customer_no"] = final_cus_no


    try:
        table = find_table_details(data)
        json_dct["LineDetails"] = table
    except:
        json_dct["LineDetails"] = []

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
                dct["invoice_currency"] = x[i].strip().split(":")[-1].strip()
                x[i] = x[i][:x[i].index("INVOICE")]
                json_dct["Header"] = dct
            # print(x[i])
            except:
                continue


        elif "CASE TOTAL" in x[i]:
            try:
                invoice_am["case_total"] = x[i].strip().split(":")[-1].strip()
            except:
                continue

        elif "GST @10%" in x[i]:
            try:
                invoice_am["gst"] = x[i].strip().split(":")[-1].strip()
            except:
                continue

        elif "INVOICE TOTAL" in x[i]:
            try:
                invoice_am["invoicetotal"] = " ".join(x[i].strip().split(":")[-1].strip().split()).strip()
            except:
                continue
        json_dct["InvoiceAmountDetails"] = invoice_am

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
        json_dct["deliveredto"] = " ".join(lst).strip()
        lst = [i.strip() for i in x[receiver_start_index: receiver_end_index]]
        json_dct["mailto"] = " ".join(lst).strip()
    except:
        pass

    return json_dct
