from flask import Flask, request, jsonify, abort
import requests
import json

app = Flask(__name__)

# এই রুটটি Vercel-এ '/'-তে ম্যাপ হবে, যা আপনার API-এর মূল Endpoint.
# আমরা এটিকে GET রিকোয়েস্টের জন্য তৈরি করছি, যেখানে URL একটি Query Parameter হিসেবে আসবে।
@app.route('/', methods=['GET'])
def get_download_info():
    """
    ইউজার কর্তৃক প্রদত্ত YouTube URL (query parameter 'url'-এর মাধ্যমে) ব্যবহার করে 
    ssvid.app এ POST রিকোয়েস্ট করে এবং JSON রেসপন্স রিটার্ন করে।
    """
    
    # 1. 'url' query parameter থেকে ভিডিও লিঙ্ক নেওয়া
    video_url = request.args.get('url')
    
    # URL না থাকলে 400 Bad Request রেসপন্স দেওয়া
    if not video_url:
        return jsonify({
            "error": "Missing URL",
            "message": "Please provide a YouTube video URL using the 'url' query parameter."
        }), 400

    # 2. আপনার মূল স্ক্রিপ্ট থেকে নেওয়া প্রয়োজনীয় ভ্যালুগুলো
    cookies = {
        # এই কুকিজগুলো সময়সাপেক্ষে মেয়াদ উত্তীর্ণ হতে পারে বা পরিবর্তন হতে পারে
        '_ga': 'GA1.1.629536978.1759997878',
        '_ga_6LBJSB3S9E': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
        '_ga_4GK2EGV9LP': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
        '_ga_GZNX0NRT3R': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
        '_ga_KM2F3J46SD': 'GS2.1.s1761037614$o8$g0$t1761037641$j33$l0$h0',
    }

    headers = {
        # Headers are crucial for a successful request to the target site
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://ssvid.app',
        'referer': 'https://ssvid.app/en30',
        # User-Agent is important to mimic a real browser
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {'hl': 'en'}
    
    # 'query' ফিল্ডে ইউজার থেকে পাওয়া URL টি ব্যবহার হচ্ছে
    data = {
        'query': video_url, 
        'cf_token': '',
        'vt': 'home',
    }
    
    target_url = 'https://ssvid.app/api/ajax/search'

    # 3. মূল POST রিকোয়েস্টটি সম্পাদন করা
    try:
        response = requests.post(
            target_url, 
            params=params, 
            cookies=cookies, 
            headers=headers, 
            data=data,
            timeout=15 # রিকোয়েস্টের জন্য সময়সীমা নির্ধারণ
        )
        
        # HTTP স্ট্যাটাস কোড (4xx, 5xx) এর জন্য ব্যতিক্রম (Exception) তৈরি করে
        response.raise_for_status() 
        
        # 4. রেসপন্সটি JSON হিসেবে রিটার্ন করা
        try:
            # যদি রেসপন্স JSON ফরম্যাটে থাকে
            return jsonify(response.json())
        except json.JSONDecodeError:
            # যদি JSON না হয়, তবে Raw Text-কে ডেটা ফিল্ডে রেখে JSON হিসেবে রিটার্ন করা
            return jsonify({
                "status": "success", 
                "data": response.text, 
                "message": "Returned raw text (not standard JSON) from external API."
            })

    except requests.exceptions.HTTPError as e:
        # 4xx বা 5xx ত্রুটি হ্যান্ডেল করা
        return jsonify({
            "error": "External API Error", 
            "message": str(e), 
            "status_code": response.status_code
        }), response.status_code
    
    except requests.exceptions.RequestException as e:
        # অন্যান্য রিকোয়েস্ট বা নেটওয়ার্ক ত্রুটি হ্যান্ডেল করা
        return jsonify({
            "error": "Internal Server Error", 
            "message": f"Error forwarding request to external service: {e}"
        }), 500

# এই লাইনটি শুধু স্থানীয়ভাবে (locally) কোড রান করার জন্য প্রয়োজনীয়
if __name__ == '__main__':
    app.run(debug=True)
