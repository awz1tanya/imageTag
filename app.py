from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/tag": {"origins": [
    "https://lovable-ai-persona-chat.lovable.app",
    "https://*.lovableproject.com",
    "https://*.lovable.app"]}})

DEFAULT_API_KEY = "AIzaSyBWpPkPeCAqX_ua_AOgHiDUmuBmhvkvbLk"
DEFAULT_MODEL = "models/gemini-1.5-flash-latest"

@app.route('/tag', methods=['POST'])
def tag_from_ai_reply():
    data = request.json
    ai_reply = data.get('ai_reply', '')
    api_key = data.get('api_key', DEFAULT_API_KEY)
    model_name = data.get('model', DEFAULT_MODEL)

    if not ai_reply.strip():
        return jsonify({"error": "Missing ai_reply"}), 400

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    tag_list = """
greeting, kiss, slap, teasing, flirting, shy, confident, seductive_gaze, romantic_tension, whisper,
fingering, thrusting, oral_sex, deep_kiss, biting_lip, licking, sucking_breast, sucking_penis,
grabbing_waist, hand_on_breast, hand_on_thigh, pulling_hair, neck_kiss, pin_against_wall,
mounted_position, cowgirl_position, doggy_position, missionary_position, spread_legs,
ride_on_top, bend_over_position, leg_wrap, leg_lift, back_arched, slow_tease, climax_building,
saree, blouse_and_saree, ghagra_choli, salwar_kameez, kurti_and_jeans, t_shirt_and_jeans,
crop_top, tank_top, short_skirt, long_skirt, bodycon_dress, backless_dress,
off_shoulder_dress, sleeveless_top, deep_neckline, bikini, lingerie, nightie, gown,
braless, no_panty,
strip_starting, strip_slowly, unbuttoning, pulling_down_skirt, pulling_down_panty,
bra_sliding_off, undressing_completely, seductive_peek, strip_one_by_one, strip_tease_mode,
mirror_view, over_the_shoulder, shy_smile, flirty_wink, panting, breathless, arching_back,
spreading_thighs, holding_sheet, fingers_between_legs, touching_self, moaning, eye_contact,
wet_dress, dress_transparent, chest_visible, nipples_visible, thighs_visible,
back_visible, cleavage_visible, waist_visible, seductive_pose, side_pose, open_mouth
"""

    prompt = f"""
Analyze the following AI girlfriend reply:

\"{ai_reply}\"

From the following list of tags:
{tag_list}

Return 1 or 2 tags that best describe the visual, mood, or erotic elements suggested in the AI response. Choose tags that reflect dress state, gestures, posture, or sexual suggestion.

Output only the tag values as comma-separated text like this:
sucking_breast, bra_sliding_off
"""

    response = model.generate_content(prompt)
    tags = response.text.strip().lower().replace('\n', '').replace('.', '')

    return jsonify({
        "tags": tags
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
