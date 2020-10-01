import pdftotext
import re

def read_text(lst):
    text = lst[0][:lst[0].index("A Finance charge will be imposed by")]
    for i in range(1, len(lst)):
        start_index = lst[i].index("AMT") + 3
        # try:
        # end_index = lst[i].index("TOTAL NET SALE USD")
        end_index = lst[i].index("A Finance charge will be imposed by")
        z = lst[i][start_index:end_index]
        # except ValueError:
        #     z = lst[i][start_index:]
        text += "\n" + z
    return text


def remove_header_footer(lst):
    for i in range(len(lst)):
        #footer
        try:
            # if "A Finance charge will be imposed by use of a periodic rate of one and one−half percent (1 1/2 %)" in lst[i]:
            #     lst.remove(lst[i])
            # elif "annual percentage rate of eighteen percent (18%), on balances over thirty (30) days old." in lst[i]:
            #     lst.remove(lst[i])
            # #header
            if "INVOICE" == lst[i].strip():
                lst[i] = re.sub("INVOICE", " ", lst[i])
            elif "UniCarriers Americas Corporation" in lst[i]:
                lst[i] = re.sub("UniCarriers Americas Corporation", " ", lst[i])
            elif "240 N. Prospect Street − Marengo, IL 60152−3298" in lst[i]:
                lst[i] = re.sub("240 N. Prospect Street − Marengo, IL 60152−3298", " ", lst[i])
            elif "Remit To: P.O.Box 70700 − Chicago, IL 60673−0700" in lst[i]:
                lst[i] = re.sub("Remit To: P.O.Box 70700 − Chicago, IL 60673−0700", " ", lst[i])

            elif "Billing Inquiries (815) 568−0061" in lst[i]:
                lst[i] = lst[i].split("568−0061")[-1]

        except:
            continue

    for i in lst:
        if len(i.strip()) == 0:
            lst.remove(i)
    return lst




#to find Invoice and UAC number
def find_invoice_uac_no(lst):
    '''
    lst : splited list of all extracted text wit "\n"
    '''
    for i in lst:
        if "Invoice Number" in i:
            invoice_index =  lst.index(i) +1
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

    for i, j in enumerate(lst_table):
        lst = j.split()

        if len(lst) >= 5 and lst[0] != "Comments":
            table_details.append({"modelpart": lst[0],
                                "description": " ".join(lst[1:-3]),
                                "quantity": lst[-3],
                                "unitprice":lst[-2],
                                "extendedamt":lst[-1]})
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
    
    bit = False
    header_dct = {}
    invoice_am_dt = {}

    with open(PDF, "rb") as f:
        pdf = pdftotext.PDF(f)

    final_lst = []
    if len(pdf) == 1:
        data = pdf[0]
    else:
        data = read_text(pdf)

    lst = data.split("\n")
    for i in lst:
        if "UniCarriers Americas Corporation" in i:
            bit = True

    if bit:
        json_dct = {"supplier":"unicarriers","LineDetails":[],"InvoiceAmountDetails":[]}
        # x = lst
        x = remove_header_footer(lst)
        invoice_index, uac_index = find_invoice_uac_no(x)
        ind = find_invoice_date_table(x)
        try:
            header_dct["invoicenumber"] = x[invoice_index].strip()
            header_dct["ucaorderno"] = x[uac_index].strip().split()[-1].strip()
            header_dct["invoicedate"] = x[ind].strip().split()[0].strip()
            header_dct["customerordernumber"] = x[ind].strip().split()[1].strip()
            header_dct["paymenttearms"] =  " ".join(x[ind].strip().split()[2:]).strip()
            header_dct["shipdate"] = x[ind+2].strip().split()[0].strip()
            header_dct["shipvia"] = x[ind+2].strip().split()[1].strip()
            header_dct["shipmenttearms"] = x[ind+2].strip().split()[2].strip()

            json_dct["Header"] = header_dct
        except:
            json_dct["header"] = []
        try:
            address_1, address_2 = add_1_2(x)
            address_1 = "".join(address_1.split("Sold To:")).strip()
            address_2 = "".join(address_2.split("Ship To:")).strip()
            json_dct["soldto"] = address_1.strip()
            json_dct["shipto"] =  address_2.strip()
        except:
            json_dct["soldto"] = ""
            json_dct["shipto"] = ""

        try:
            line_details_under_tabe = line_details(x)
            json_dct["LineDetails"] = line_details_under_tabe

            dct = invoice_amount_details(x)
            json_dct["InvoiceAmountDetails"] = {
                "totalnetsaleusd": dct["TOTAL NET SALE USD"].strip(),
                "freight": dct["FREIGHT"].strip(),
                "taxamountusd": dct["TAX AMOUNT USD"],
                "totalnetamountusd":dct["TOTAL NET AMOUNT USD"],
                "paymentdueby": dct["PAYMENT DUE BY"]
            }

        except:
            json_dct["InvoiceAmountDetails"] = {}

        return json_dct
        
    else:
        return {"response":"Please upload pdf only for Unicareers/Australia's supplier for POC"}

