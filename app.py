from flask import Flask, request, jsonify, abort
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO) # লগিং চালু করা

# টার্গেট URL ও রেফারার
REFERER_URL = 'https://ssvid.app/en30'
TARGET_API_URL = 'https://ssvid.app/api/ajax/search'

# কমন হেডার্স
BASE_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://ssvid.app',
    'referer': REFERER_URL,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

@app.route('/', methods=['GET'])
def get_download_info():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({
            "error": "Missing URL",
            "message": "Please provide a YouTube video URL using the 'url' query parameter."
        }), 400

    try:
        # 1. ডায়নামিক কুকিজ সংগ্রহের জন্য প্রাথমিক GET রিকোয়েস্ট
        logging.info("Step 1: Fetching dynamic cookies from referer page...")
        session = requests.Session()
        
        # Referer-এ হিট করে সেশন কুকিজগুলো নেওয়া
        # এই রিকোয়েস্টটির হেডার্স POST রিকোয়েস্টের তুলনায় সামান্য ভিন্ন হতে পারে
        initial_response = session.get(REFERER_URL, headers={'User-Agent': BASE_HEADERS['user-agent']}, timeout=10)
        initial_response.raise_for_status()
        
        dynamic_cookies = session.cookies.get_dict()
        logging.info(f"Step 1 Success. Found cookies: {list(dynamic_cookies.keys())}")

        # 2. POST রিকোয়েস্টের জন্য প্রস্তুতি
        post_headers = BASE_HEADERS.copy() # কপি করে নেয়া যাতে BASE_HEADERS অপরিবর্তিত থাকে
        
        # পূর্বের স্থির কুকিজগুলো (যদি প্রয়োজন হয়) dynamic_cookies-এর সাথে মার্জ করা যেতে পারে
        # তবে সেশন থেকে পাওয়া কুকিজই যথেষ্ট হওয়া উচিত।

        params = {'hl': 'en'}
        
        data = {
            'query': video_url, 
            'cf_token': '', # এটিও ডায়নামিকভাবে নিতে হতে পারে, কিন্তু এখন খালি রাখা হলো
            'vt': 'home',
        }
        
        # 3. ডায়নামিক কুকিজ সহ মূল POST রিকোয়েস্টটি সম্পাদন করা
        logging.info("Step 2: Sending POST request with dynamic cookies...")
        response = session.post(
            TARGET_API_URL, 
            params=params, 
            cookies=dynamic_cookies, # এখানে ডায়নামিক কুকিজ ব্যবহার হচ্ছে
            headers=post_headers, 
            data=data,
            timeout=15 
        )
        response.raise_for_status() 
        
        # 4. রেসপন্স রিটার্ন করা
        try:
            return jsonify(response.json())
        except json.JSONDecodeError:
            return jsonify({
                "status": "success", 
                "data": response.text, 
                "message": "Returned raw text (not standard JSON) from external API."
            })

    except requests.exceptions.RequestException as e:
        # রিকোয়েস্ট ত্রুটি হ্যান্ডেল করা
        error_message = f"Error in external service interaction: {e}"
        logging.error(error_message)
        
        status_code = getattr(e.response, 'status_code', 500)
        
        return jsonify({
            "error": "Request Failed", 
            "message": error_message,
            "status_code": status_code
        }), status_code

if __name__ == '__main__':
    app.run(debug=True)
