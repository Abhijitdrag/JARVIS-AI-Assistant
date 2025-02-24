# import asyncio
# from random import randint
# from PIL import Image
# import requests
# from dotenv import get_key
# import os
# from time import sleep

# def open_images(prompt):
#     folder_path = r"Data"
#     prompt = prompt.replace(" ", "_")

#     Files = [f"{prompt}{i}.jpg" for i in range (1,5)]

#     for jpg_file in Files:
#         image_path = os.path.join(folder_path, jpg_file)

#         try:
#             img = Image.open(image_path)
#             print(f"Opening image:{image_path}")
#             img.show()
#             sleep(1)
        
#         except IOError:
#             print(f"Unable to open {image_path}")

# API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
# headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# async def query(payload):
#     response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
#     return response.content

# async def generate_images(prompt : str):
#     tasks = []

#     for _ in range(4):
#         payload = {
#             "input": f"{prompt}, quality=4K, sharpness=maximum , Ultra High details , high resolution, seed = {randint(0, 1000000)}",

#         }
#         task = asyncio.create_task(query(payload))
#         tasks.append(task)

#     image_bytes_list = await asyncio.gather(*tasks)

#     for i, image_bytes in enumerate(image_bytes_list):
#         with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
#             f.write(image_bytes)

# def GenerateImages(prompt: str):
#     asyncio.run(generate_images(prompt))
#     open_images(prompt)

# while True:
#     try:
#         with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
#             Data : str = f.read()
            
#         prompt, Status = Data.split(",")

#         if Status == "True":
#             print("Genrating Images....")
#             ImageStatus = GenerateImages(prompt=prompt)

#             with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
#                 f.write("False,False")
#                 break
            
#         else:
#             sleep(1)
            
#     except Exception as e:
#         print(f"Error: {e}")
#         sleep(1)

import asyncio
import os
import requests
from random import randint
from time import sleep
from PIL import Image
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

DATA_FOLDER = "Data"
DATA_FILE = "Frontend/Files/ImageGeneration.data"

async def query(payload):
    """Sends a request to the Hugging Face API."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

async def generate_images(prompt: str):
    """Generates 4 images asynchronously and saves them."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    tasks = []
    
    for i in range(4):
        payload = {
            "input": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(query(payload))
    
    image_bytes_list = await asyncio.gather(*tasks)
    
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(DATA_FOLDER, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

    open_images(prompt)

def open_images(prompt: str):
    """Opens the generated images."""
    prompt = prompt.replace(" ", "_")
    
    for i in range(1, 5):
        image_path = os.path.join(DATA_FOLDER, f"{prompt}{i}.jpg")
        
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1)
            except IOError:
                print(f"Unable to open {image_path}")
        else:
            print(f"Image not found: {image_path}")

async def main():
    """Continuously checks the data file for new prompts to generate images."""
    while True:
        try:
            with open(DATA_FILE, "r") as f:
                data = f.read().strip()
            
            if not data:
                await asyncio.sleep(1)
                continue
            
            prompt, status = data.split(",")
            
            if status.strip().lower() == "true":
                print("Generating Images...")
                await generate_images(prompt)
                
                with open(DATA_FILE, "w") as f:
                    f.write("False,False")
                break
            else:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
