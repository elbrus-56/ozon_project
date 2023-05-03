from connector.config import *


def _make_sku_party(value: str):
    res = value.split('_')
    if len(res) == 2:
        return res[0], int(res[1])


# from connector.ctest import tst_get_data
# tst_get_data()
def tst_get_data():
    from connector.ozon_manager import OzonManager
    service = OzonManager()
    res = service.get_orders_by_status(days=15)
    print('type:', type(res))
    print(res)


def _modify_ozon_response(arr):
    data = None
    try:
        data = arr.get('additional_data')
    except:
        pass
    if data:
        for dat in data:
            new_data = []
            products = None
            try:
                posting_number = dat.get('posting_number')
                products = dat.get('products')
            except:
                pass
            if products:
                new_products = []
                for product in products:
                    com_offer_id = None
                    try:
                        com_offer_id = product.get('offer_id')
                        sku, party = _make_sku_party(com_offer_id)
                        price = product.get('price')
                        del product['sku']
                    except:
                        pass
                    if com_offer_id:
                        price = float(price)
                        price = float(int(price * 100)) / 100
                        product['price'] = price
                        product['sku'] = sku
                        product['party'] = party
                    new_products.append(product)
            new_data.append(dict(
                posting_number=posting_number,
                products=new_products
            ))
        return new_data


# from connector.ctest import tst_send_info_to_1c
#  tst_send_info_to_1c()
def tst_send_info_to_1c():
    """Посылаем тестовый запрос в 1С"""
    import json
    url = TUSMK_URL
    input_from_ozon = """{
        "result": ["50829078-0083-1"],
        "additional_data": [{"posting_number": "50829078-0083-1",
        "products": [{"price": "50.000000",
        "offer_id": "И00016556_1",
        "name": "Наконечник НШвИ 4-12 КВТ",
        "sku": 833066856,
        "quantity": 1,
        "mandatory_mark": [""],
        "currency_code": "RUB"}]}]
        }"""
    res = json.loads(input_from_ozon)
    res = _modify_ozon_response(res)
    print('res:', res)
    # print(type(res))


# from connector.ctest import tst_send_pdf
#  tst_send_pdf()

def tst_send_pdf():
    """читаю и отправляю файл"""
    import requests
    document = "58448248-0007-2"
    document1 = "67209962-0008-1"
    file_name = document + ".pdf"
    file1_name = document1 + ".pdf"
    res = {}
    send_data = dict(
        posting_number=document,
        url=file_name
    )
    arr_send = []
    arr_send.append(send_data)
    file = open(f"{STATIC_PATH}{document}.pdf", "rb")
    url = TUSMK_URL + TUSMK_SEND_PDF_LABEL
    res[document] = file
    if file:
        print('---- has ===')
        files = {file_name: open(f"{STATIC_PATH}{document}.pdf", "rb"),
                 file1_name: open(f"{STATIC_PATH}{document1}.pdf", "rb")}
        response = requests.post(url, data={"file": file_name, "file1": file1_name}, files=files)
        # response = requests.post(url, data=send_data, files=res)
    else:
        print('--none ----')
    file.close()
    print(response)


# response = requests.post(url, data={"chat_id": CHANNEL_ID}, files={"document": document})

# from connector.ctest import tst_send_acts
# tst_send_acts()
def tst_send_acts():
    """"""
    from connector.tusmk import TusMK
    service = TusMK()
    act_id = "10868744"
    service.send_doc_to_tus(f"{STATIC_PATH}{act_id}.pdf", act_id)


# from connector.ctest import tst_send_label
# tst_send_label()
def tst_send_label():
    """"""
    from connector.tusmk import TusMK
    service = TusMK()
    sending_pdfs = []
    sending_pdfs.append(dict(
        posting_number="04027198-0162-2",
        file=f"{STATIC_PATH}04027198-0162-2.pdf"
    ))
    service.send_labels(sending_pdfs)
