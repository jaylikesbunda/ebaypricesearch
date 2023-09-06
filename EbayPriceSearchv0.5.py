import requests
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

def search_dvd():
    api_endpoint = "https://svcs.ebay.com/services/search/FindingService/v1"
    app_id = "DeclanFe-DVDPrice-PRD-e0f245140-b42120d4"
    
    headers = {
        "Content-Type": "application/json",
        "X-EBAY-SOA-OPERATION-NAME": "findItemsAdvanced",
        "X-EBAY-SOA-SECURITY-APPNAME": app_id,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON"
    }

    keywords = keywords_entry.get()
    selected_category_name = category_var.get()
    selected_category_id = category_ids[selected_category_name]

    params = {
        "keywords": keywords,
        "categoryId": selected_category_id,
        "paginationInput.entriesPerPage": 10
    }

    try:
        response = requests.get(api_endpoint, headers=headers, params=params)
        response.raise_for_status()

        response_data = response.json()

        if "findItemsAdvancedResponse" in response_data:
            results_text.delete(1.0, tk.END)
            results_text.insert(tk.END, json.dumps(response_data, indent=2))
            
            average_price = calculate_average_price(response_data)
            average_price_label.config(text=f"Average Price: ${average_price:.2f} USD")
            
            display_first_listing(response_data)
            display_first_image(response_data)
        else:
            messagebox.showerror("Error", "No data found in the response.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Request Error", f"Request to eBay failed: {str(e)}")
    except json.JSONDecodeError as e:
        messagebox.showerror("JSON Parsing Error", f"Unable to parse JSON response: {str(e)}")

def calculate_average_price(response_data):
    item_sum = 0
    item_count = 0
    
    search_result = response_data["findItemsAdvancedResponse"][0].get("searchResult", [{}])[0]
    items = search_result.get("item", [])
    
    for item in items:
        current_price = float(item["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"])
        item_sum += current_price
        item_count += 1
    
    if item_count > 0:
        average_price = item_sum / item_count
        return average_price
    else:
        return 0.0

def display_first_listing(response_data):
    search_result = response_data["findItemsAdvancedResponse"][0].get("searchResult", [{}])[0]
    items = search_result.get("item", [])
    
    if items:
        first_item = items[0]
        title = first_item.get("title", [""])[0]
        
        if title:
            title_label.config(text=f"Title: {title}")
        else:
            title_label.config(text="Title not available")

def display_first_image(response_data):
    search_result = response_data["findItemsAdvancedResponse"][0].get("searchResult", [{}])[0]
    items = search_result.get("item", [])
    
    if items:
        first_item = items[0]
        gallery_url = first_item.get("galleryURL", [""])[0]
        
        if gallery_url:
            img = Image.open(requests.get(gallery_url, stream=True).raw)
            img.thumbnail((200, 200))
            img = ImageTk.PhotoImage(img)
            
            image_label.config(image=img)
            image_label.image = img
        else:
            image_label.config(image="")
    else:
        image_label.config(image="")

root = tk.Tk()
root.title("eBay DVD Search")

# Create a frame for the search section
search_frame = ttk.Frame(root, padding=10)
search_frame.pack(fill="x")

# Search Section Heading
search_label = ttk.Label(search_frame, text="Search DVDs", font=("Helvetica", 16))
search_label.pack()

# Keywords Entry
keywords_label = ttk.Label(search_frame, text="Enter keywords:")
keywords_label.pack(anchor="w")
keywords_entry = ttk.Entry(search_frame, width=40)
keywords_entry.pack(fill="x", pady=5)

# Category Dropdown
category_label = ttk.Label(search_frame, text="Select a category:")
category_label.pack(anchor="w")

# Define eBay category IDs for the desired categories
category_ids = {
    "DVDs & Movies": 11232,
    "DVDs & Blu-ray Discs": 617,
    "Film Stock": 63821,
    "Laserdiscs": 381,
    "UMDs": 132975,
    "VHS Tapes": 309,
    "Other Formats": 41676,
    "Storage & Media Accessories": 52554,
}

# Convert category names to a list for the dropdown menu
category_names = list(category_ids.keys())

category_var = tk.StringVar()
category_var.set(category_names[0])  # Default category
category_dropdown = ttk.Combobox(search_frame, textvariable=category_var, values=category_names, state="readonly")
category_dropdown.pack(fill="x", pady=5)

# Search Button
search_button = ttk.Button(search_frame, text="Search", command=search_dvd)
search_button.pack()

# Create a frame for the results section
results_frame = ttk.Frame(root, padding=10)
results_frame.pack(fill="both", expand=True)

# Results Section Heading
results_label = ttk.Label(results_frame, text="Search Results", font=("Helvetica", 16))
results_label.pack()

# Image Label
image_label = ttk.Label(results_frame, text="Image will be displayed here")
image_label.pack(pady=5)

# Title Label
title_label = ttk.Label(results_frame, text="", font=("Helvetica", 12))
title_label.pack()

# Average Price Label
average_price_label = ttk.Label(results_frame, text="Average Price: $0.00 USD", font=("Helvetica", 12))
average_price_label.pack(pady=10)

# Results Text
results_text = ScrolledText(results_frame, wrap=tk.WORD, width=80, height=20)
results_text.pack(fill="both", expand=True)

root.mainloop()
