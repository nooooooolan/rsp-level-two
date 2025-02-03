from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.HTTP import HTTP
from csv import DictReader
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    # browser.configure(
    #     slowmo=1,
    # )
    open_robot_order_website()
    close_annoying_modal()
    orders = download_and_get_orders()
    
    for row in orders:
        fill_order_and_submit(row)
    
    archive()


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

        
def download_and_get_orders():
    http = HTTP()
    # verify = False to ignore SSL certificate, super dangerous but this is just a test
    res = http.download("https://robotsparebinindustries.com/orders.csv", verify=False, overwrite=True)
    csv_reader = DictReader(res.text.split("\n"), delimiter=",")
    csv = list(csv_reader)
    table = Tables()
    return table.create_table(csv)
    

def close_annoying_modal():
    page=browser.page()
    page.click("text=OK")


def fill_order_and_submit(order):
    
    # Fill the form one by one
    page = browser.page()
    
    page.select_option("#head", order["Head"])
    
    # press tab based on the body number
    
    if order["Body"] == "1":
        press_bot(1)  
    elif order["Body"] == "2":
        press_bot(2)  
    elif order["Body"] == "3":
        press_bot(3)
    elif order["Body"] == "4":
        press_bot(4)
    elif order["Body"] == "5":
        press_bot(5)
    elif order["Body"] == "6":
        press_bot(6)
   
    page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#order")
    while "Error" in page.content():
        page.click("#order")
                
    save_full_summary(order["Order number"])
    page.click("#order-another")
    close_annoying_modal()
    
def press_bot(number): 
    page=browser.page()
    page.click(f"#id-body-{number}")

def screenshot_robot(order_number):
    page = browser.page()
    path = f"output/previews/robot_order_png_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=path)
    return path
    

def store_receipt_as_pdf(order_number):
    page = browser.page()
    page.screenshot()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    path = f"output/receipts/robot_order_pdf_{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, path)
    return path

# reciept is pdf and screenshot is png
def embed_screenshot_to_receipt(receipt_path, screenshot_path):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot_path], target_document=receipt_path, append=True)
    

def save_full_summary(order_number):
    receipt_path = store_receipt_as_pdf(order_number)
    screenshot_path = screenshot_robot(order_number)
    embed_screenshot_to_receipt(receipt_path, screenshot_path)

def check_order_not_succesful():
    page = browser.page()
    #check if #order is present
    page.click("#order")
    return page.locator("#order").is_present()

def archive():
    archive = Archive()
    archive.archive_folder_with_zip(folder="./output/receipts", archive_name="./output/final_receipts.zip")

# def combine_screenshot_and_reciept(order):
#     pdf = PDF()
#     reciept_path = save_reciept(order)
#     screenshot_path = save_screenshot(order)
#     pdf.embed_image_to_pdf(screenshot_path, reciept_path, reciept_path)
#     return reciept_path