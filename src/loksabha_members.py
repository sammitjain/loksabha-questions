import fitz
import io
from PIL import Image
import pandas as pd


def extract_members_info():
    loksabha_members_file = "data/loksabha_members.xlsx"
    df = pd.read_excel(loksabha_members_file)
    loksabha_members_list = df.values.tolist()
    return loksabha_members_list


def extract_images():
    loksabha_members_file = "data/loksabha_members_with_pictures.pdf"
    pdf_file = fitz.open(loksabha_members_file)
    member_num = 1
    for page_index in range(len(pdf_file)):
        # get the page itself
        page = pdf_file[page_index]
        image_list = page.getImageList()
        # printing number of images found in this page
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            print("[!] No images found on page", page_index)
        for image_index, img in enumerate(page.getImageList(), start=1):
            if member_num in [99, 325]:
                # no image for Number 99. Check PDF
                member_num += 1
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = pdf_file.extractImage(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # save it to local disk
            image.save(open(f"data/img/image_{member_num}.{image_ext}", "wb"))
            member_num += 1

