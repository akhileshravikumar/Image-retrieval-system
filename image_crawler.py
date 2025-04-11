import os
import json
import requests

#  Your API key
PEXELS_API_KEY = "bkfbFmPgNt2T3NJxGlQhfEljWyLDGbehiczrpvNB7h1QhwOZy1f6g0Hk"
QUERY = "Animals"
SAVE_FOLDER = "static/images"
TOTAL_IMAGES = 1000
PER_PAGE = 80  # Pexels limit
HEADERS = {"Authorization": PEXELS_API_KEY}

os.makedirs(SAVE_FOLDER, exist_ok=True)
image_metadata = []
image_count = 0
page = 1

print(f" Searching for '{QUERY}' images...")

while image_count < TOTAL_IMAGES:
    print(f" Fetching page {page}...")
    url = f"https://api.pexels.com/v1/search?query={QUERY}&per_page={PER_PAGE}&page={page}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f" Error: {response.status_code} {response.text}")
        break

    data = response.json()
    photos = data.get("photos", [])
    if not photos:
        print(" No more images available.")
        break

    for photo in photos:
        image_url = photo["src"]["large"]
        image_name = f"img_{image_count + 1}.jpg"
        image_path = os.path.join(SAVE_FOLDER, image_name)

        try:
            img_response = requests.get(image_url, timeout=10)
            if img_response.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(img_response.content)

                image_metadata.append({
                    "image": image_name,
                    "alt": photo.get("alt", ""),
                    "title": QUERY,
                    "context": photo["photographer"],
                    "source_url": photo["url"]
                })

                print(f" Downloaded: {image_name}")
                image_count += 1
            else:
                print(f" Skipped {image_name} (status {img_response.status_code})")
        except Exception as e:
            print(f" Error downloading {image_url}: {e}")

        if image_count >= TOTAL_IMAGES:
            break
    page += 1

#  Save metadata
with open("static/image_metadata.json", "w", encoding="utf-8") as f:
    json.dump(image_metadata, f, indent=2, ensure_ascii=False)

print(f"\n Finished downloading {image_count} images to '{SAVE_FOLDER}'")
