from flask import Flask, Response, jsonify
import requests
import json
import logging

app = Flask(__name__)

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)

# --- ইউজার কর্তৃক প্রদত্ত স্থির ভ্যালুগুলো ---
TARGET_API_URL = 'https://ssvid.app/api/ajax/search'

# Cookies
STATIC_COOKIES = {
    '_ga': 'GA1.1.629536978.1759997878',
    '_ga_6LBJSB3S9E': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
    '_ga_4GK2EGV9LP': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
    '_ga_GZNX0NRT3R': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
    '_ga_KM2F3J46SD': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
}

# Headers
STATIC_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://ssvid.app',
    'priority': 'u=1, i',
    'referer': 'https://ssvid.app/en30',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

# Query Parameters
STATIC_PARAMS = {
    'hl': 'en',
}

# POST Data
STATIC_DATA = {
    'query': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # স্থির YouTube URL
    'cf_token': '',
    'vt': 'home',
}
# ----------------------------------------------


@app.route('/', methods=['GET', 'POST'])
def execute_request():
    """
    রুট এন্ডপয়েন্টে হিট করলেই সরাসরি স্থির রিকোয়েস্টটি এক্সিকিউট করে রেসপন্স রিটার্ন করে।
    """
    
    try:
        logging.info("Executing static request to ssvid.app...")
        
        # 1. স্থির প্যারামিটার্স সহ POST রিকোয়েস্ট
        response = requests.post(
            TARGET_API_URL, 
            params=STATIC_PARAMS, 
            cookies=STATIC_COOKIES, 
            headers=STATIC_HEADERS, 
            data=STATIC_DATA,
            timeout=15 
        )
        
        # 2. রেসপন্সটির স্ট্যাটাস কোড এবং কনটেন্ট টাইপ বজায় রেখে ক্লায়েন্টকে ফেরত দেওয়া
        # যেহেতু target API সম্ভবত JSON রিটার্ন করে, তাই আমরা সরাসরি content এবং header ব্যবহার করব।
        
        return Response(
            response.content,
            status=response.status_code,
            headers={
                'Content-Type': response.headers.get('Content-Type', 'application/json')
            }
        )

    except requests.exceptions.RequestException as e:
        # রিকোয়েস্ট বা নেটওয়ার্ক ত্রুটি হ্যান্ডেল করা
        error_message = f"Request Failed: {e}"
        logging.error(error_message)
        
        return jsonify({
            "error": "Internal Server Error", 
            "message": error_message,
            "details": "Check if the hardcoded cookies/headers are still valid."
        }), 500

if __name__ == '__main__':
    # শুধুমাত্র স্থানীয়ভাবে (locally) রান করার জন্য
    app.run(debug=True)
