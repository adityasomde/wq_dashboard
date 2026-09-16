import os
import re
import requests

BASE_URL = "https://platform.worldquantbrain.com"
DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'dist')

def download_and_patch():
    print(f"Ensuring {DIST_DIR} exists...")
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Download index.html
    print("Downloading index.html...")
    res = requests.get(BASE_URL)
    res.raise_for_status()
    html_content = res.text
    
    # Extract asset URLs
    print("Extracting JS and CSS assets...")
    # Find scripts
    scripts = re.findall(r'src="(/static/js/[^"]+)"', html_content)
    # Find css
    styles = re.findall(r'href="(/static/css/[^"]+)"', html_content)
    
    # Some assets might just be in the root (like /favicon-32x32.png)
    # The UI loads them dynamically or via html. For now, let's just rewrite the html 
    # to prepend the absolute URL for things we don't download, 
    # OR we just download everything. Let's just download the static JS and CSS for now.
    
    assets = scripts + styles
    
    for asset in assets:
        asset_url = f"{BASE_URL}{asset}"
        asset_path = os.path.join(DIST_DIR, asset.lstrip('/'))
        os.makedirs(os.path.dirname(asset_path), exist_ok=True)
        
        print(f"Downloading {asset_url}...")
        asset_res = requests.get(asset_url)
        asset_res.raise_for_status()
        
        content = asset_res.text
        
        # Patch JS files!
        if asset.endswith('.js'):
            print(f"Patching {asset}...")
            # Replace api.worldquantbrain.com with localhost:5000/proxy
            content = content.replace("api.worldquantbrain.com", "localhost:5000/proxy")
            # Also if there are hardcoded https://api.worldquantbrain.com, the above replaces the domain.
            
        with open(asset_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # Save index.html
    # We don't need to patch the HTML because the script/link tags are relative /static/...
    # which we downloaded perfectly into our dist/static/ folder.
    index_path = os.path.join(DIST_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print("Done downloading and patching WQ Brain frontend!")

if __name__ == "__main__":
    download_and_patch()
