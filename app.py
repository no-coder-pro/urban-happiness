from flask import Flask, request, jsonify, abort
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# টার্গেট API URL
TARGET_API_URL = 'https://ssvid.app/api/ajax/search'
REFERER_URL = 'https://ssvid.app/en30'

# ম্যানুয়ালি সাজানো কুকিজ ডিকশনারি
STATIC_COOKIES = {
    "AMCV_8AD56F28618A50850A495FB6%40AdobeOrg__cloudflare.com": "MCMID|90882946568727837095374330991471658028",
    "CF_VERIFIED_DEVICE_d2af84c597699c97a5e19da69f21f7c0e9f5fa9b2dce8c317b709eb73548b01e__cloudflare.com": "1759045465",
    "OptanonConsent__cloudflare.com": "isGpcEnabled=0&datestamp=Mon+Oct+20+2025+08%3A53%3A35+GMT%2B0600+(Bangladesh+Standard+Time)&version=202503.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=e5242c83-8ec9-47fb-a24a-5aa4227ae616&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&AwaitingReconsent=false",
    "__cf_logged_in__cloudflare.com": "1",
    "__q_state_37pXYrro6wCZbsU7__cloudflare.com": "eyJ1dWlkIjoiNDAxNDE0Y2QtNTU0ZC00MmZkLTliMTktMWUxNTc0NzYwNmM3IiwiY29va2llRG9tYWluIjoiY2xvdWRmbGFyZS5jb20iLCJtZXNzZW5nZXJFeHBhbmRlZCI6bnVsbCwicHJvbXB0RGlzbWlzc2VkIjpmYWxzZSwiY29udmVyc2F0aW9uSWQiOm51bGx9",
    "_biz_flagsA__cloudflare.com": "%7B%22Version%22%3A1%2C%22ViewThrough%22%3A%221%22%2C%22Mkto%22%3A%221%22%2C%22XDomain%22%3A%221%22%2C%22Ecid%22%3A%22-574770400%22%7D",
    "_biz_nA__cloudflare.com": "5",
    "_biz_pendingA__cloudflare.com": "%5B%5D",
    "_biz_uid__cloudflare.com": "280fd539ca3e4516e65e666765d25829",
    "_ga__cloudflare.com": "GA1.1.d4a2fa26-57c6-4cbe-ac4c-829e9153eaa5",
    "_ga__ssvid.app": "GA1.1.629536978.1759997878",
    "_ga_4GK2EGV9LP__ssvid.app": "GS2.1.s1761037614$o8$g1$t1761039359$j59$l0$h0",
    "_ga_6LBJSB3S9E__ssvid.app": "GS2.1.s1761037614$o8$g1$t1761039359$j59$l0$h0",
    "_ga_GZNX0NRT3R__ssvid.app": "GS2.1.s1761037614$o8$g1$t1761039359$j59$l0$h0",
    "_ga_KM2F3J46SD__ssvid.app": "GS2.1.s1761037614$o8$g1$t1761039359$j59$l0$h0",
    "_ga_SQCRB0TXZW__cloudflare.com": "GS2.1.s1759057165$o1$g0$t1759057174$j51$l0$h0",
    "_gcl_au__cloudflare.com": "1.1.1835693499.1759057165",
    "_mkto_trk__cloudflare.com": "id:713-XSC-918&token:_mch-cloudflare.com-81b6666b1078faacd9473989cfdf0c75",
    "_uetvid__cloudflare.com": "33300a509c5a11f0841061e79f9a2af5|169s4rr|1759057167916|1|1|bat.bing.com/p/insights/c/q",
    "cfz_adobe__cloudflare.com": "%7B%22MsVJ_ecid%22%3A%7B%22v%22%3A%22CiY5MDg4Mjk0NjU2ODcyNzgzNzA5NTM3NDMzMDk5MTQ3MTY1ODAyOFIOCIzZnfqYMyoDVkE2MALwAYzZnfqYMw%22%2C%22e%22%3A1793173510560%7D%7D",
    "cfz_amplitude__cloudflare.com": "%7B%22TTin_event_id%22%3A%7B%22v%22%3A%226%22%2C%22e%22%3A1792464846445%7D%2C%22TTin_device_id%22%3A%7B%22v%22%3A%22dc23f7bf-e2fe-4fa5-9932-8e9bb7819572%22%2C%22e%22%3A1790593165090%7D%7D",
    "cfz_facebook-pixel__cloudflare.com": "%7B%22OwdI_fb-pixel%22%3A%7B%22v%22%3A%22fb.2.1759045448420.1671138808%22%2C%22e%22%3A1790581448420%7D%2C%22VVgx_fb-pixel%22%3A%7B%22v%22%3A%22fb.2.1759045448420.630580828%22%2C%22e%22%3A1790581448420%7D%2C%22bHox_fb-pixel%22%3A%7B%22v%22%3A%22fb.2.1759045448420.1133941904%22%2C%22e%22%3A1790581448420%7D%2C%22elKW_fb-pixel%22%3A%7B%22v%22%3A%22fb.2.1759045448420.822517974%22%2C%22e%22%3A1790581448420%7D%2C%22dzQR_fb-pixel%22%3A%7B%22v%22%3A%22fb.2.1759045469415.2043080948%22%2C%22e%22%3A1790581469415%7D%7D",
    "cfz_google-analytics_v4__cloudflare.com": "%7B%22nzcr_ga4%22%3A%7B%22v%22%3A%22d4a2fa26-57c6-4cbe-ac4c-829e9153eaa5%22%2C%22e%22%3A1792464865221%7D%2C%22nzcr_engagementDuration%22%3A%7B%22v%22%3A%220%22%2C%22e%22%3A1792464865221%7D%2C%22nzcr_engagementStart%22%3A%7B%22v%22%3A%221760928865221%22%2C%22e%22%3A1792464865221%7D%2C%22nzcr_counter%22%3A%7B%22v%22%3A%2235%22%2C%22e%22%3A1792464865221%7D%2C%22nzcr_session_counter%22%3A%7B%22v%22%3A%222%22%2C%22e%22%3A1792464865221%7D%2C%22nzcr__z_ga_audiences%22%3A%7B%22v%22%3A%22d4a2fa26-57c6-4cbe-ac4c-829e9153eaa5%22%2C%22e%22%3A1790581469415%7D%2C%22nzcr_let%22%3A%7B%22v%22%3A%221760928865221%22%2C%22e%22%3A1792464865221%7D%2C%22nzcr_ga4sid%22%3A%7B%22v%22%3A%22198800713%22%2C%22e%22%3A1760930665221%7D%7D",
    "cfz_reddit__cloudflare.com": "%7B%22fZaD_reddit_uuid%22%3A%7B%22v%22%3A%221759057159729.3d744660-aed5-4312-8e61-d23b483ecc92%22%2C%22e%22%3A1790593159729%7D%7D",
    "kndctr_8AD56F28618A50850A495FB6_AdobeOrg_identity__cloudflare.com": "CiY5MDg4Mjk0NjU2ODcyNzgzNzA5NTM3NDMzMDk5MTQ3MTY1ODAyOFIOCIzZnfqYMyoDVkE2MALwAYzZnfqYMw==",
    "sparrow_id__cloudflare.com": "{\"deviceId\":\"0eaf7fd3-3200-492c-9f5f-4d7963792e5a\"}",
    "zaraz-consent__cloudflare.com": "{\"Tuku\":true,\"aMDT\":true}"
}

# হেডার্স
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
        return jsonify({"error": "Missing URL", "message": "Please provide a YouTube video URL using the 'url' query parameter."}), 400

    params = {'hl': 'en'}
    
    data = {
        'query': video_url, 
        'cf_token': '', 
        'vt': 'home',
    }
    
    try:
        logging.info("Sending POST request with manually provided cookies...")
        
        # 1. ম্যানুয়াল কুকিজ ব্যবহার করে সরাসরি POST রিকোয়েস্ট
        response = requests.post(
            TARGET_API_URL, 
            params=params, 
            cookies=STATIC_COOKIES, # <--- নতুন কুকিজ
            headers=BASE_HEADERS, 
            data=data,
            timeout=15 
        )
        response.raise_for_status() 
        
        # 2. রেসপন্স রিটার্ন করা
        try:
            return jsonify(response.json())
        except json.JSONDecodeError:
            return jsonify({
                "status": "success", 
                "data": response.text, 
                "message": "Returned raw text (not standard JSON) from external API."
            })

    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 500)
        return jsonify({
            "error": "External API Error", 
            "message": f"HTTP Error {status_code}: Check if the cookies are still valid.", 
            "status_code": status_code
        }), status_code
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Internal Server Error", "message": f"Request failed: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
