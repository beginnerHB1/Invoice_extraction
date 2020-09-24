import pdftotext
import re

#to find Invoice and UAC number
def remove_header_footer(lst):
    for i in range(len(lst)):
        #footer
        if "A Finance charge will be imposed by use of a periodic rate of one and one−half percent (1 1/2 %)" in lst[i]:
            lst.remove(lst[i])
        elif "annual percentage rate of eighteen percent (18%), on balances over thirty (30) days old." in lst[i]:
            lst.remove(lst[i])
        #header
        elif "INVOICE" == lst[i].strip():
            lst[i] = re.sub("INVOICE", " ", lst[i])
        elif "UniCarriers Americas Corporation" in lst[i]:
            lst[i] = re.sub("UniCarriers Americas Corporation", " ", lst[i])
        elif "240 N. Prospect Street − Marengo, IL 60152−3298" in lst[i]:
            lst[i] = re.sub("240 N. Prospect Street − Marengo, IL 60152−3298", " ", lst[i])
        elif "Remit To: P.O.Box 70700 − Chicago, IL 60673−0700" in lst[i]:
            lst[i] = re.sub("Remit To: P.O.Box 70700 − Chicago, IL 60673−0700", " ", lst[i])

        elif "Billing Inquiries (815) 568−0061" in lst[i]:
            lst[i] = lst[i].split("568−0061")[-1]
            break

    for i in lst:
        if len(i.strip()) == 0:
            lst.remove(i)
    return lst

def find_invoice_uac_no(lst):
    '''
    lst : splited list of all extracted text wit "\n"
    '''
    for i in lst:
        if "Invoice Number" in i:
            invoice_index =  lst.index(i) + 2
        elif "UCA Order No." in i:
            uac_index = lst.index(i) + 1

    return invoice_index, uac_index

#to find Invoice Date, ...
def find_invoice_date_table(lst):
    for i in lst:
        if "Invoice Date" in i.strip():
            return lst.index(i) + 1

def find_address_indexes(lst):
    '''
    lst : splited list of all extracted text wit "\n"

    info:
    To find start and end index of address(sold_to and ship_to)
    '''
    for i in lst:
        if "Sold To" in i:
            start_index = lst.index(i)
        elif "Invoice Date" in i:
            end_index = lst.index(i)
    return start_index, end_index


def add_1_2(lst):
    '''
    lst : splited list of all extracted text wit "\n"
    '''
    start, end =  find_address_indexes(lst)
    address_lst = lst[start:end]

    address_1 = ''
    address_2 = ''
    for i in range(len(address_lst)):
        lst = address_lst[i].split(" ")
        index_lst = []
        '''
        To find start and end of address 1 from lst indexes
        '''
        for i in range(len(lst)):
            try:
                if lst[i] != "" and (lst[i+1] != "" or lst[i+2] != ""):
                    # print(lst.index(lst[i]))
                    index_lst.append(lst.index(lst[i]))
                    start_index_add_1 = lst.index(lst[i])
                    break
            except:
                break

        for i in range(1, len(lst[start_index_add_1:])):
            try:
                if lst[i] == "" and lst[i-1] == "":
                    end_index_add_1 = start_index_add_1 + lst[start_index_add_1:].index(lst[i])
                    add = lst[start_index_add_1:end_index_add_1]
                    break
            except ValueError:
                add = lst[start_index_add_1:]
                break

        address_1 += " " + " ".join(add)

        lst = lst[end_index_add_1:]
        address_2 += " " + " ".join(lst).strip()
    return address_1.strip(), address_2.strip()


def line_details(lst):
    '''
    To find details under table Model or Part #, Description, Quantity, Unit Price, Extended AMT
    '''
    for i in lst:
        if "TOTAL NET SALE USD" in i:
            end_index = lst.index(i)
        elif "Model or Part #" in i:
            start_index = lst.index(i) + 1
    lst_table = lst[start_index:end_index]
    table_details = []

    for j in range(len(lst_table)):
        removing_elements = []#to remove repeted values in list
        lst = lst_table[j].split(" ")
        table = []

        #to find all 5 values
        for i in range(len(lst)):
            try:
                if lst[i] != "":
                    if lst[i+1] != "":
                        table.append(lst[i] + " " + lst[i+1])
                        removing_elements.append(lst[i+1])
                    else:
                        table.append(lst[i])

            except IndexError:
                table.append(lst[i])
                break
        for i in removing_elements:
            table.remove(i)
        table_details.append({f"Model or Part #_{j}": table[0], f"Description_{j}": table[1], f"Quantity_{j}": table[2], f"Unit_Price_{j}":table[3], f"Extended_AMT_{j}":table[4]})

    return table_details

#total amount
def invoice_amount_details(lst):
    for i in lst:
        if "PAYMENT DUE BY" in i:
            end_index = lst.index(i)
        elif "TOTAL NET SALE USD" in i:
            start_index = lst.index(i)

    details_lst = lst[start_index:end_index+1]

    amount_details_dict = {}
    if len(details_lst) == 4:
        for i in range(3):
            key = " ".join(details_lst[i].split()[:-1])
            val = details_lst[i].split()[-1]
            amount_details_dict[key] = val

        lst = details_lst[3].split()
        key = " ".join(lst[:3])
        val = lst[3]
        amount_details_dict[key] = val

        key = " ".join(lst[4:-1])
        val = lst[-1]
        amount_details_dict[key] = val
    return amount_details_dict

def create_json(lst_det):
    return {"Field Name":lst_det[0],
            "length": lst_det[1],
            "Mandotory":lst_det[2],
            "Sample Value":lst_det[3]}

def extract_detail(PDF):
    json_dct = {"Header":[],"Sold To":[],"Ship To":[], "Line Details (Repeated Segment)":[], "Invoice Amount Details":[]}
    with open(PDF, "rb") as f:
        pdf = pdftotext.PDF(f)

    final_lst = []

    data = pdf[0]

    #spliting from new line
    lst = data.split("\n")
    x = remove_header_footer(lst)
    invoice_index, uac_index = find_invoice_uac_no(x)
    try:
        json_dct["Header"].append(create_json(["Invoice Number", len(x[invoice_index].strip()), "yes", x[invoice_index].strip()]))
        json_dct["Header"].append(create_json(["UCA Order No.", len(x[uac_index].strip().split()[-1]), "yes", x[uac_index].strip().split()[-1]]))

        ind = find_invoice_date_table(x)

        json_dct["Header"].append(create_json(["Invoice Date",  "mmddyyyy", "yes", x[ind].strip().split()[0]]))
        json_dct["Header"].append(create_json(["Customer Order Number", len(x[ind].strip().split()[1]), "yes", x[ind].strip().split()[1]]))
        json_dct["Header"].append(create_json(["Payment Terms", len(" ".join(x[ind].strip().split()[2:])), "yes", " ".join(x[ind].strip().split()[2:])]))
        json_dct["Header"].append(create_json(["Ship Date", "mmddyyyy", "yes", x[ind+2].strip().split()[0]]))
        json_dct["Header"].append(create_json(["Ship Via", len(x[ind+2].strip().split()[1]), "yes", x[ind+2].strip().split()[1]]))
        json_dct["Header"].append(create_json(["Shipment Terms", len(x[ind+2].strip().split()[2]), "yes", x[ind+2].strip().split()[2]]))
    except:
        json_dct["Header"] = []

    try:
        address_1, address_2 = add_1_2(x)
        address_1 = "".join(address_1.split("Sold To:")).strip()
        address_2 = "".join(address_2.split("Ship To:")).strip()
        json_dct["Sold To"].append(create_json(["Sold to","", "yes", address_1]))
        json_dct["Ship To"].append(create_json(["Ship to","", "yes", address_2]))
    except:
        json_dct["Sold To"] = []
        json_dct["Ship To"] = []

    try:
        line_details_under_tabe = line_details(x)
        for i in line_details_under_tabe:
            for j in list(i.keys()):
                json_dct["Line Details (Repeated Segment)"].append(create_json([j, len(i[j]), "yes", i[j]]))

        dct = invoice_amount_details(x)
        for i in list(dct.keys()):
            if i == "PAYMENT DUE BY":
                json_dct["Invoice Amount Details"].append(create_json([i, "mmddyyyy", "yes", dct[i]]))
            else:
                json_dct["Invoice Amount Details"].append(create_json([i, len(dct[i]), "yes", dct[i]]))
    except:
        json_dct["Invoice Amount Details"] = []
        
    return json_dct
