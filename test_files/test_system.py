
from datetime import date
import os
import shutil
from extract_all import extract_all


def get_new_wb_name():
    return date.today().strftime("%B %d, %Y")
 
def mv_to_pdf_folder(di,ndi):
    for file in os.listdir(di):
        if 'pdf' in os.path.splitext(file)[1].lower():
            shutil.move(os.path.join(di,file),os.path.join(ndi,os.path.basename(file)))
            print(file,ndi)

if __name__ == '__main__':
    data_url = 'data/unzipped'
    new_data_url = 'data/pdf'
    mv_to_pdf_folder(data_url,new_data_url)
    data_url = new_data_url
    df = extract_all(data_url)
    if not os.path.exists('../data/xlsx'):
        os.mkdir('../data/xlsx')
    
    print('Exporting data to xlsx')
    # code.interact(local=dict(globals(),**locals()))
    df.to_excel('../data/xlsx/'+get_new_wb_name()+'.xlsx')
    print('All done!')