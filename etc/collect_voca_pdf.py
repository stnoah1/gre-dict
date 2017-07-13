import pdfplumber

table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "text",
    "intersection_x_tolerance": 15
}


def get_pdf():
    pdf = pdfplumber.open("data/강상홍_voca.pdf")
    table_data = []
    for index, page in enumerate(pdf.pages):
        if index < 6:
            continue
        # if index == 8:
        #     break
        table_data += page.extract_table()
        print(page.extract_table())

    # table_data = list(zip(*table_data))
    # print(table_data)
get_pdf()
