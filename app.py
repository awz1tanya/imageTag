from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import csv
import random

app = Flask(__name__)
CORS(app, resources={r"/tag": {"origins": [
    "https://lovable-ai-persona-chat.lovable.app",
    "https://*.lovableproject.com",
    "https://*.lovable.app",
    "https://lovable-ai-friends.lovable.app"
]}})

DEFAULT_API_KEY = "AIzaSyDyn8p6mIfjX5LxSTRUEhZnLsncYT68Fyw"
DEFAULT_MODEL = "models/gemini-1.5-flash-latest"
CSV_PATH = "imageTag.csv"

# Load CSV to dictionary {(ai_name, tag): [gif urls]}
def load_image_tag_csv():
    mapping = {}
    for_ai_names = set()
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 3:
                ai_name = row[0].strip().lower()
                tag = row[1].strip().lower()
                urls = [url.strip() for url in row[2:] if url.strip()]
                mapping[(ai_name, tag)] = urls
                for_ai_names.add(ai_name)
    return mapping, for_ai_names

tag_url_map, all_ai_names = load_image_tag_csv()

@app.route('/tag', methods=['POST'])
def tag_from_ai_reply():
    data = request.json
    ai_reply = data.get('ai_reply', '')
    ai_name = data.get('ai_name', '').strip().lower()

    if not ai_reply:
        return jsonify({"error": "Missing ai_reply"}), 400

    # Fallback to Prachi if ai_name is not available
    if ai_name not in all_ai_names:
        ai_name = 'prachi'

    # Filter available tags for this ai_name
    relevant_tags = {tag for (name, tag) in tag_url_map if name == ai_name}

    # Gemini API Call
    genai.configure(api_key=DEFAULT_API_KEY)
    model = genai.GenerativeModel(DEFAULT_MODEL)

    prompt = f"""
Analyze the following AI girlfriend reply:

\"{ai_reply}\"

From the following list of tags:
{"greeting", "kiss", "slap", "teasing", "flirting", "shy", "confident", "seductive_gaze", "romantic_tension", "whisper",
"fingering", "thrusting", "oral_sex", "deep_kiss", "biting_lip", "licking", "sucking_breast", "sucking_penis",
"grabbing_waist", "hand_on_breast", "hand_on_thigh", "pulling_hair", "neck_kiss", "pin_against_wall",
"mounted_position", "cowgirl_position", "doggy_position", "missionary_position", "spread_legs",
"ride_on_top", "bend_over_position", "leg_wrap", "leg_lift", "back_arched", "slow_tease", "climax_building",
"saree", "blouse_and_saree", "ghagra_choli", "salwar_kameez", "kurti_and_jeans", "t_shirt_and_jeans",
"crop_top", "tank_top", "short_skirt", "long_skirt", "bodycon_dress", "backless_dress",
"off_shoulder_dress", "sleeveless_top", "deep_neckline", "bikini", "lingerie", "nightie", "gown",
"braless", "no_panty",
"strip_starting", "strip_slowly", "unbuttoning", "pulling_down_skirt", "pulling_down_panty",
"bra_sliding_off", "undressing_completely", "seductive_peek", "strip_one_by_one", "strip_tease_mode",
"mirror_view", "over_the_shoulder", "shy_smile", "flirty_wink", "panting", "breathless", "arching_back",
"spreading_thighs", "holding_sheet", "fingers_between_legs", "touching_self", "moaning", "eye_contact",
"wet_dress", "dress_transparent", "chest_visible", "nipples_visible", "thighs_visible",
"back_visible", "cleavage_visible", "waist_visible", "seductive_pose", "side_pose", "open_mouth"}

Return 1 or 2 tags that best describe the visual, mood, or erotic elements suggested in the AI response.
Only output tags as comma-separated text like this:
sucking_breast, bra_sliding_off
"""

    response = model.generate_content(prompt)
    tags = response.text.strip().lower().replace('\n', '').replace('.', '')
    tag_array = [tag.strip() for tag in tags.split(',') if tag.strip() in relevant_tags]

    result_urls = []
    for tag in tag_array:
        urls = tag_url_map.get((ai_name, tag), [])
        if urls:
            result_urls.append(random.choice(urls))
        if len(result_urls) >= 2:
            break

    return jsonify({
        "ai_name": ai_name,
        "tags": ', '.join(tag_array),
        "images": ', '.join(result_urls)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
