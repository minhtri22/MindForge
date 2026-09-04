#!/usr/bin/env python3
import hashlib, json, random, re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

SEED = 20260904
RNG = random.Random(SEED)
BENCHMARK_VERSION = "1.0"
MATERIALIZATION_REVISION = "r1-semantic-correction"
ROOT = Path(__file__).resolve().parents[1] / "benchmarks" / "track-a-capability-v1"
ROOT.mkdir(parents=True, exist_ok=True)

FAMILIES = [f"A{i}" for i in range(1, 8)]
SPLIT_COUNTS = {"calibration": 40, "development": 60, "test": 100}
LANG_QUOTAS = {
    "calibration": {"vi": 24, "vi_en": 10, "en": 6},
    "development": {"vi": 36, "vi_en": 15, "en": 9},
    "test": {"vi": 60, "vi_en": 25, "en": 15},
}
DIFF_QUOTAS = {
    "calibration": {"straightforward": 16, "contextual": 14, "adversarial": 10},
    "development": {"straightforward": 24, "contextual": 21, "adversarial": 15},
    "test": {"straightforward": 40, "contextual": 35, "adversarial": 25},
}

# Test cases 0..39 are 20 controlled pairs. Pair-member attributes are identical.
TEST_PAIR_LANGS = ["vi"] * 12 + ["vi_en"] * 5 + ["en"] * 3
TEST_PAIR_DIFFS = ["straightforward"] * 8 + ["contextual"] * 7 + ["adversarial"] * 5
RNG.shuffle(TEST_PAIR_LANGS); RNG.shuffle(TEST_PAIR_DIFFS)

CONTACTS = [
    {"id": "c_linh", "name": "Linh", "relation": "partner"},
    {"id": "c_tuan", "name": "Tuấn", "relation": "coworker", "project": "A"},
    {"id": "c_tuan_anh", "name": "Tuấn Anh", "relation": "friend"},
    {"id": "c_mai", "name": "Mai", "relation": "sister"},
]
ACTIONS = [
    {"id": "maps", "kind": "navigation"}, {"id": "messages", "kind": "messaging"},
    {"id": "phone", "kind": "calling"}, {"id": "calendar", "kind": "calendar"},
    {"id": "notes", "kind": "notes"},
]
EXTERNAL = ["web_search", "general_qa", "travel_search", "news_search"]

PHRASES = {
"A1": {
 "calibration": {
  "NAVIGATE": [("Chỉ đường về nhà", "mở Maps chỉ đường về nhà", "Navigate home"), ("Dẫn tôi về nhà", "route me về nhà", "Route me home")],
  "MESSAGE": [("Nhắn Linh là tôi về muộn", "nhắn Linh: I'm running late", "Message Linh that I'm running late"), ("Báo Linh tôi tới trễ", "message Linh là tôi tới late", "Tell Linh I'll arrive late")],
  "CALL": [("Gọi Tuấn bên dự án A", "call Tuấn của project A", "Call Tuan from project A")],
  "REMIND": [("Nhắc tôi 8 giờ tưới cây", "remind me 8 giờ tưới cây", "Remind me at 8 to water the plants")],
  "LOCAL_TRANSFORM": [("Rút gọn câu này: Tôi sẽ đến muộn khoảng mười phút", "shorten câu này: tôi sẽ đến muộn 10 phút", "Shorten this: I will arrive about ten minutes late")],
  "LOOKUP_DELEGATE": [("Tìm giá vàng hôm nay", "check giá vàng today", "Look up today's gold price")],
  "APP_ACTION": [("Mở ghi chú", "open app Ghi chú", "Open Notes")],
  "CLARIFY": [("Gửi cho anh ấy nhé", "send cái này cho anh ấy", "Send this to him")],
 },
 "development": {
  "NAVIGATE": [("Mở đường về nhà giúp tôi", "cho tôi route về home", "Give me directions home"), ("Tìm lộ trình về nhà", "find route về nhà", "Find a route home")],
  "MESSAGE": [("Gửi Linh tin tôi sẽ về trễ", "text Linh là tối nay tôi về late", "Text Linh that I'll be home late")],
  "CALL": [("Điện cho Tuấn ở dự án A", "phone Tuấn bên project A", "Phone Tuan on project A")],
  "REMIND": [("Đặt nhắc 20 giờ tưới cây", "set reminder 20h tưới cây", "Set a reminder for 20:00 to water plants")],
  "LOCAL_TRANSFORM": [("Viết ngắn lại: Tôi sẽ ghé qua sau giờ làm", "make this shorter: tôi sẽ ghé qua sau work", "Make this shorter: I will stop by after work")],
  "LOOKUP_DELEGATE": [("Tra thời tiết Đà Nẵng ngày mai", "check weather Đà Nẵng tomorrow", "Check tomorrow's weather in Da Nang")],
  "APP_ACTION": [("Mở lịch cho tôi", "open Calendar giúp tôi", "Open Calendar")],
  "CLARIFY": [("Gọi cho người đó", "call người đó giúp tôi", "Call that person")],
 },
 "test": {
  "NAVIGATE": [("Cho tôi đường về nhà từ đây", "show me đường về home từ đây", "Show me the way home from here"), ("Từ chỗ này đi về nhà thế nào?", "how do I get về nhà from here?", "How do I get home from here?")],
  "MESSAGE": [("Báo cho Linh biết tôi chậm khoảng mười phút", "tell Linh tôi sẽ late khoảng 10 phút", "Let Linh know I'm about ten minutes late")],
  "CALL": [("Nối máy với Tuấn của nhóm dự án A", "connect me với Tuấn from project A", "Put me through to Tuan on project A")],
  "REMIND": [("Tạo nhắc việc tưới cây lúc 7 giờ tối", "make reminder tưới cây at 7pm", "Create a reminder to water plants at 7 pm")],
  "LOCAL_TRANSFORM": [("Làm gọn câu sau: Cuộc họp có thể bắt đầu muộn vài phút", "make concise: cuộc họp có thể start muộn", "Make concise: The meeting may start a few minutes late")],
  "LOOKUP_DELEGATE": [("Kiểm tra chuyến bay VN210 hôm nay có trễ không", "check flight VN210 hôm nay có delay không", "Check whether flight VN210 is delayed today")],
  "APP_ACTION": [("Mở ứng dụng lịch", "launch app Calendar", "Launch the Calendar app")],
  "CLARIFY": [("Nhắn cho người lúc nãy", "message người lúc nãy", "Message the person from earlier")],
 }
},
}

# Natural code-mix is deliberately restrained: use common digital verbs/nouns rather than word-by-word mixing.
def trilang(lang, triple): return {"vi": triple[0], "vi_en": triple[1], "en": triple[2]}[lang]

def quota_array(counts):
    a=[]
    for k,v in counts.items(): a += [k]*v
    RNG.shuffle(a); return a

def split_attrs(split):
    n=SPLIT_COUNTS[split]
    if split != "test": return quota_array(LANG_QUOTAS[split]), quota_array(DIFF_QUOTAS[split])
    pair_langs=[x for x in TEST_PAIR_LANGS for _ in (0,1)]
    pair_diffs=[x for x in TEST_PAIR_DIFFS for _ in (0,1)]
    rem_lang={k:LANG_QUOTAS[split][k]-Counter(pair_langs)[k] for k in LANG_QUOTAS[split]}
    rem_diff={k:DIFF_QUOTAS[split][k]-Counter(pair_diffs)[k] for k in DIFF_QUOTAS[split]}
    return pair_langs + quota_array(rem_lang), pair_diffs + quota_array(rem_diff)

def base_fixture(global_i):
    return {
      "current_context": {
        "date_local": str(date(2026,1,1)+timedelta(days=global_i)),
        "time_local": f"{7+(global_i%13):02d}:{(global_i*11)%60:02d}",
        "location": ["home","office","outside"][global_i%3],
        "device_state": {"network": "online" if global_i%4 else "offline"},
      },
      "personal_state": {
        "home_label":"home", "home_address":"12 Nguyễn Trãi, Hà Nội", "partner":"Linh",
        "contacts": json.loads(json.dumps(CONTACTS, ensure_ascii=False)),
        "preferred_navigation_app":"maps", "preferred_language":"vi",
      },
      "available_actions": json.loads(json.dumps(ACTIONS)),
      "available_local_capabilities": ["device_context"],
      "external_capabilities": list(EXTERNAL),
    }

def add_surface_noise(text, idx, diff, lang):
    # Bounded variation; avoid duplicated politeness artifacts.
    if diff == "straightforward": return text
    low=text.lower().strip()
    suffixes_vi=[" nhé", " giúp tôi", " được không", " luôn nhé"]
    suffixes_en=[" please", " for me", " if you can", " now"]
    if diff == "contextual":
        choices=suffixes_en if lang=="en" else suffixes_vi
        for j in range(len(choices)):
            suffix=choices[(idx+j)%len(choices)]
            token=suffix.strip().lower()
            if token not in low and not (token.endswith('nhé') and low.endswith('nhé')):
                return text+suffix
        return text
    # adversarial: punctuation/casing/noise, not gibberish
    if idx%3==0: return text.replace("?", "") + ("..." if not text.endswith(".") else "")
    if idx%3==1: return text[0].lower()+text[1:] if text else text
    suffix=" pls" if lang=="en" else " nha"
    return text if suffix.strip().lower() in low else text+suffix

def provenance(fam, split, mode, variant):
    prefix={"calibration":"C","development":"D","test":"H"}[split]
    return {
      "truth_source":"rule_defined",
      "generator":"scripts/materialize_track_a_v1_r1.py",
      "generator_seed":SEED,
      "materialization_revision":MATERIALIZATION_REVISION,
      "review_status":"semantic_r1_pass_final_frozen",
      "scenario_id":f"{fam}-{prefix}-S{mode:02d}",
      "template_id":f"{fam}-{prefix}-T{mode:02d}-V{variant:02d}",
    }

def phrase_a1(split, intent, lang, idx):
    pool=PHRASES["A1"][split][intent]
    return trilang(lang, pool[idx%len(pool)])

def make_regular(fam, split, local_i, lang, diff, global_i):
    f=base_fixture(global_i); inp={"user_utterance":"", **f}; tags=[]; exp={}; scoring={}
    # split-specific mode offsets reduce composition reuse, while preserving label coverage.
    offset={"calibration":0,"development":3,"test":7}[split]
    if fam=="A1":
        labels=["NAVIGATE","MESSAGE","CALL","REMIND","LOCAL_TRANSFORM","LOOKUP_DELEGATE","APP_ACTION","CLARIFY"]
        intent=labels[(local_i+offset)%len(labels)]
        text=phrase_a1(split,intent,lang,local_i)
        inp["user_utterance"]=add_surface_noise(text,local_i,diff,lang)
        exp={"intent_label":intent}; scoring={"primary":"intent_label"}
        if intent=="CLARIFY": tags += ["ambiguous_pronoun","clarification_required"]
        mode=labels.index(intent)
    elif fam=="A2":
        mode=(local_i+offset)%6
        if mode==0:
            t=("Nhắn cho vợ là tôi về muộn", "text my vợ là tối nay tôi về muộn", "Message my partner that I'll be late")
            exp={"entity_mentions":["vợ" if lang!="en" else "my partner"],"resolved_entity_ids":["c_linh"],"resolved_values":["Linh"],"clarification_required":False}
        elif mode==1:
            # Exact full-name Tuấn must resolve despite Tuấn Anh also existing.
            t=("Gọi Tuấn", "call Tuấn giúp tôi", "Call Tuan")
            exp={"entity_mentions":["Tuấn" if lang!="en" else "Tuan"],"resolved_entity_ids":["c_tuan"],"resolved_values":["Tuấn"],"clarification_required":False}
        elif mode==2:
            # Genuine ambiguity: two contacts with identical display name.
            inp["personal_state"]["contacts"]=[
              {"id":"c_mai_sister","name":"Mai","relation":"sister"},
              {"id":"c_mai_vendor","name":"Mai","relation":"vendor"},
              {"id":"c_linh","name":"Linh","relation":"partner"},]
            t=("Gọi Mai", "call Mai giúp tôi", "Call Mai")
            exp={"entity_mentions":["Mai"],"resolved_entity_ids":[],"resolved_values":[],"clarification_required":True}; tags += ["similar_entity_names","clarification_required"]
        elif mode==3:
            t=("Chỉ đường về nhà", "route về home", "Navigate home")
            exp={"entity_mentions":["nhà" if lang!="en" else "home"],"resolved_entity_ids":["home"],"resolved_values":["12 Nguyễn Trãi, Hà Nội"],"clarification_required":False}
        elif mode==4:
            inp["personal_state"].update({"favorite_cafe":"quán Cây","favorite_cafe_address":"8 Phan Đình Phùng, Hà Nội"})
            t=("Đi tới quán cà phê tôi hay ngồi", "navigate tới my usual cafe", "Navigate to my usual cafe")
            exp={"entity_mentions":["quán cà phê tôi hay ngồi" if lang!="en" else "my usual cafe"],"resolved_entity_ids":["favorite_cafe"],"resolved_values":["8 Phan Đình Phùng, Hà Nội"],"clarification_required":False}
        else:
            inp["personal_state"].update({"current_work_location":"18 Láng Hạ, Hà Nội","former_work_location":"1 Tràng Tiền, Hà Nội"})
            t=("Chỉ đường tới chỗ làm hiện tại", "navigate tới current workplace", "Navigate to my current workplace")
            exp={"entity_mentions":["chỗ làm hiện tại" if lang!="en" else "my current workplace"],"resolved_entity_ids":["current_work_location"],"resolved_values":["18 Láng Hạ, Hà Nội"],"clarification_required":False}; tags += ["stale_personal_fact"]
        inp["user_utterance"]=add_surface_noise(trilang(lang,t),local_i,diff,lang); scoring={"primary":"entity_set_f1","secondary":["resolved_value_accuracy"]}
    elif fam=="A3":
        mode=(local_i+offset)%6
        if mode==0:
            inp["personal_state"]["preferred_navigation_app"]="maps"; t=("Về nhà bằng ứng dụng tôi vẫn dùng", "về home bằng app tôi hay dùng", "Go home using my usual navigation app")
            exp={"interpretation_label":"NAVIGATE_HOME_WITH_PREFERRED_APP","normalized":{"destination":"home","app":"maps"}}
        elif mode==1:
            t=("Trả lời bằng ngôn ngữ tôi ưu tiên", "reply bằng preferred language của tôi", "Reply in my preferred language")
            exp={"interpretation_label":"RESPOND_VI","normalized":{"language":"vi"}}
        elif mode==2:
            inp["current_context"]["device_state"]["network"]="offline"; t=("Tìm đường về nhà nhưng máy đang mất mạng", "route về nhà while offline", "Route me home while the device is offline")
            exp={"interpretation_label":"NAVIGATE_HOME_OFFLINE_CONSTRAINT","normalized":{"destination":"home","network":"offline"}}; tags += ["context_preference_conflict"]
        elif mode==3:
            inp["personal_state"].update({"former_work_location":"District 1","current_work_location":"District 3"}); t=("Đi tới văn phòng hiện tại của tôi", "navigate tới current office", "Navigate to my current office")
            exp={"interpretation_label":"CURRENT_WORK_LOCATION","normalized":{"work_location":"District 3"}}; tags += ["stale_personal_fact"]
        elif mode==4:
            inp["personal_state"]["morning_destination"]="gym"; inp["current_context"]["time_local"]="07:00"; t=("Đưa tôi tới chỗ tôi thường đến vào buổi sáng", "take me tới my usual morning place", "Take me to my usual morning place")
            exp={"interpretation_label":"MORNING_DESTINATION_GYM","normalized":{"destination":"gym"}}
        else:
            inp["current_context"]["conversation_language"]="en"; t=("Dùng ngôn ngữ của cuộc trò chuyện này", "use language của conversation hiện tại", "Use the language of this conversation")
            exp={"interpretation_label":"RESPOND_EN","normalized":{"language":"en"}}
        inp["user_utterance"]=add_surface_noise(trilang(lang,t),local_i,diff,lang); scoring={"primary":"normalized_interpretation_accuracy","secondary":["counterfactual_consistency"]}
    elif fam=="A4":
        mode=(local_i+offset)%6
        if mode==0:
            t=("Mở bản đồ và chỉ đường về nhà", "open Maps rồi route về nhà", "Open Maps and navigate home"); exp={"action_id":"maps"}
        elif mode==1:
            t=("Nhắn Linh là tôi đến sau 10 phút", "text Linh: tôi tới sau 10 phút", "Message Linh that I'll arrive in 10 minutes"); exp={"action_id":"messages"}
        elif mode==2:
            inp["available_actions"]=[a for a in ACTIONS if a["id"]!="maps"]; t=("Mở Maps chỉ đường về nhà", "open Maps để về home", "Open Maps and navigate home"); exp={"action_id":"NONE"}; tags += ["unavailable_tool","unsupported_action"]
        elif mode==3:
            t=("Gọi Tuấn bên dự án A", "call Tuấn bên project A", "Call Tuan from project A"); exp={"action_id":"phone"}
        elif mode==4:
            inp["available_actions"]=[{"id":"maps","kind":"navigation"},{"id":"browser","kind":"web"}]; t=("Tìm lộ trình về nhà", "find route về nhà", "Find a route home"); exp={"action_id":"maps"}; tags += ["semantically_similar_tools"]
        else:
            t=("Mở lịch", "open Calendar", "Open Calendar"); exp={"action_id":"calendar"}
        inp["user_utterance"]=add_surface_noise(trilang(lang,t),local_i,diff,lang); scoring={"primary":"action_id","secondary":["unavailable_action_false_selection"]}
    elif fam=="A5":
        mode=(local_i+offset)%6
        if mode==0:
            payload = {"vi":"tôi về muộn 20 phút", "vi_en":"I'm late 20 phút", "en":"I'll be 20 minutes late"}[lang]
            prefix = {"vi":"Nhắn Linh: ", "vi_en":"message Linh: ", "en":"Message Linh: "}[lang]
            inp["user_utterance"]=prefix+payload
            exp={"arguments":{"contact_id":"c_linh","text":payload}}
        elif mode==1:
            inp["user_utterance"]=trilang(lang,("Chỉ đường về nhà","navigate về home","Navigate home")); exp={"arguments":{"destination":"12 Nguyễn Trãi, Hà Nội"}}
        elif mode==2:
            task={"vi":"tưới cây","vi_en":"tưới cây","en":"water the plants"}[lang]
            inp["user_utterance"]=trilang(lang,("Nhắc tôi lúc 20:00 tưới cây","remind me lúc 20:00 tưới cây","Remind me at 20:00 to water the plants")); exp={"arguments":{"time":"20:00","task":task}}
        elif mode==3:
            inp["user_utterance"]=trilang(lang,("Gọi Tuấn bên dự án A","call Tuấn from project A","Call Tuan from project A")); exp={"arguments":{"contact_id":"c_tuan"}}
        elif mode==4:
            inp["user_utterance"]=trilang(lang,("Nhắn Linh","message Linh","Message Linh")); exp={"arguments":{"contact_id":"c_linh","text":None}}; tags += ["missing_required_argument"]
        else:
            inp["user_utterance"]=trilang(lang,("Tạo lịch hẹn nha sĩ ngày 12/10 lúc 09:30","create calendar nha sĩ ngày 12/10 at 09:30","Create a dentist appointment on October 12 at 09:30")); exp={"arguments":{"date":"2026-10-12","time":"09:30","title":"nha sĩ" if lang!="en" else "dentist"}}
        inp["user_utterance"]=add_surface_noise(inp["user_utterance"],local_i,diff,lang); scoring={"primary":"slot_micro_f1","secondary":["exact_record_match"],"text_policy":"literal_source_payload"}
    elif fam=="A6":
        mode=(local_i+offset)%6
        if mode==0:
            # genuine same-display-name ambiguity
            inp["personal_state"]["contacts"]=[{"id":"c_mai_sister","name":"Mai","relation":"sister"},{"id":"c_mai_vendor","name":"Mai","relation":"vendor"}]
            t=("Gọi Mai", "call Mai giúp tôi", "Call Mai"); exp={"clarification_required":True,"clarification_reason":"AMBIGUOUS_ENTITY"}; tags += ["similar_entity_names","clarification_required"]
        elif mode==1:
            t=("Nhắn Linh", "message Linh", "Message Linh"); exp={"clarification_required":True,"clarification_reason":"MISSING_ARGUMENT"}; tags += ["missing_required_argument","clarification_required"]
        elif mode==2:
            inp["current_context"]["device_state"]["network"]="offline"; t=("Tra giá vàng hôm nay khi máy đang offline", "check gold price today while offline", "Check today's gold price while the device is offline"); exp={"clarification_required":False,"clarification_reason":"NONE"}; tags += ["world_knowledge_trap"]
        elif mode==3:
            t=("Chỉ đường về nhà", "navigate về home", "Navigate home"); exp={"clarification_required":False,"clarification_reason":"NONE"}
        elif mode==4:
            t=("Gọi Tuấn", "call Tuấn", "Call Tuan"); exp={"clarification_required":False,"clarification_reason":"NONE"}
        else:
            t=("Rút gọn câu: Tôi sẽ về muộn", "shorten câu: tôi sẽ về muộn", "Shorten: I will be late"); exp={"clarification_required":False,"clarification_reason":"NONE"}
        inp["user_utterance"]=add_surface_noise(trilang(lang,t),local_i,diff,lang); scoring={"primary":"clarification_required","secondary":["under_clarification","over_clarification"]}
    else: # A7
        mode=(local_i+offset)%6
        # Semantics freeze: LOCAL_MODEL means intrinsic learned text transformation only.
        # LOCAL_APP_OR_TOOL means an explicitly listed local action/capability is required.
        if mode==0:
            t=("Rút gọn câu này: Tôi sẽ đến muộn", "shorten câu này: tôi sẽ đến muộn", "Shorten this: I will arrive late"); exp={"route":"LOCAL_MODEL"}
        elif mode==1:
            t=("Chỉ đường về nhà", "navigate về home", "Navigate home"); exp={"route":"LOCAL_APP_OR_TOOL"}
        elif mode==2:
            t=("Giá vàng hôm nay bao nhiêu?", "gold price hôm nay là bao nhiêu?", "What is today's gold price?"); exp={"route":"EXTERNAL"}; tags += ["world_knowledge_trap"]
        elif mode==3:
            t=("Gọi Mai", "call Mai", "Call Mai"); inp["personal_state"]["contacts"]=[{"id":"c_mai_1","name":"Mai"},{"id":"c_mai_2","name":"Mai"}]; exp={"route":"CLARIFY"}; tags += ["similar_entity_names","clarification_required"]
        elif mode==4:
            t=("Mở lịch của tôi", "open my Calendar", "Open my Calendar"); exp={"route":"LOCAL_APP_OR_TOOL"}
        else:
            t=("Tóm tắt câu này trong một dòng: Họp dời sang 3 giờ chiều", "summarize in one line: Họp dời sang 3 giờ chiều", "Summarize this in one line: The meeting moved to 3 pm"); exp={"route":"LOCAL_MODEL"}
        inp["user_utterance"]=add_surface_noise(trilang(lang,t),local_i,diff,lang); scoring={"primary":"route","secondary":["false_local","unnecessary_external"],"route_semantics_version":"v1-r1"}
    if lang=="vi_en": tags.append("code_mix")
    if diff=="adversarial" and not tags: tags.append(["irrelevant_personal_state","noisy_text","local_vs_external_trap"][local_i%3])
    if "irrelevant_personal_state" in tags: inp["personal_state"]["irrelevant_fact"]="thích cà phê ít đá"
    return inp,exp,scoring,sorted(set(tags)),mode

def make_counterfactual(fam, pair_idx, variant, lang, diff, global_i):
    # Start from the same base fixture for both members. Change exactly one declared input path.
    f=base_fixture(global_i-variant); inp={"user_utterance":"", **f}; tags=["counterfactual_context"]; scoring={};
    if fam=="A1":
        inp["user_utterance"]=trilang(lang,("Xử lý việc này theo ngữ cảnh ngay trước đó", "handle this theo previous context", "Handle this using the immediately previous context"))
        inp["current_context"]["foreground_reference"]="navigation" if variant==0 else "message"
        exp={"intent_label":"NAVIGATE" if variant==0 else "MESSAGE"}; scoring={"primary":"intent_label"}; changed="current_context.foreground_reference"; mode=90
    elif fam=="A2":
        inp["user_utterance"]=trilang(lang,("Liên lạc bằng cuộc gọi với Mai", "place a call tới Mai", "Place a phone call to Mai"))
        if variant==0:
            inp["personal_state"]["contacts"]=[{"id":"c_mai","name":"Mai","relation":"sister"}]
            exp={"entity_mentions":["Mai"],"resolved_entity_ids":["c_mai"],"resolved_values":["Mai"],"clarification_required":False}
        else:
            inp["personal_state"]["contacts"]=[{"id":"c_mai_sister","name":"Mai","relation":"sister"},{"id":"c_mai_vendor","name":"Mai","relation":"vendor"}]
            exp={"entity_mentions":["Mai"],"resolved_entity_ids":[],"resolved_values":[],"clarification_required":True}; tags += ["similar_entity_names","clarification_required"]
        scoring={"primary":"entity_set_f1","secondary":["resolved_value_accuracy"]}; changed="personal_state.contacts"; mode=91
    elif fam=="A3":
        inp["user_utterance"]=trilang(lang,("Chọn ngôn ngữ theo phiên hội thoại đang mở", "choose language theo active chat session", "Choose the language from the active chat session"))
        inp["current_context"]["conversation_language"]="vi" if variant==0 else "en"
        exp={"interpretation_label":"RESPOND_VI" if variant==0 else "RESPOND_EN","normalized":{"language":"vi" if variant==0 else "en"}}
        scoring={"primary":"normalized_interpretation_accuracy","secondary":["counterfactual_consistency"]}; changed="current_context.conversation_language"; mode=92
    elif fam=="A4":
        inp["user_utterance"]=trilang(lang,("Khởi chạy ứng dụng Maps để đưa tôi về nhà", "launch Maps app để guide me home", "Launch the Maps app to guide me home"))
        inp["available_actions"]=[{"id":"maps","kind":"navigation"}] if variant==0 else [{"id":"browser","kind":"web"}]
        exp={"action_id":"maps" if variant==0 else "NONE"}; scoring={"primary":"action_id","secondary":["unavailable_action_false_selection"]}; changed="available_actions"; mode=93
        if variant: tags += ["unavailable_tool"]
    elif fam=="A5":
        inp["user_utterance"]=trilang(lang,("Nhắn Linh nội dung tôi vừa đọc", "message Linh the text tôi vừa đọc", "Message Linh the text I just dictated"))
        inp["current_context"]["last_dictated_text"]="Tôi về lúc 8" if variant==0 else None
        exp={"arguments":{"contact_id":"c_linh","text":"Tôi về lúc 8" if variant==0 else None}}
        scoring={"primary":"slot_micro_f1","secondary":["exact_record_match"],"text_policy":"literal_source_payload","text_source":"current_context.last_dictated_text"}; changed="current_context.last_dictated_text"; mode=94
        if variant: tags += ["missing_required_argument"]
    elif fam=="A6":
        inp["user_utterance"]=trilang(lang,("Kết nối cuộc gọi tới Mai", "connect a call tới Mai", "Connect a call to Mai"))
        inp["personal_state"]["contacts"]=[{"id":"c_mai","name":"Mai"}] if variant==0 else [{"id":"c_mai_1","name":"Mai"},{"id":"c_mai_2","name":"Mai"}]
        exp={"clarification_required":bool(variant),"clarification_reason":"AMBIGUOUS_ENTITY" if variant else "NONE"}
        scoring={"primary":"clarification_required","secondary":["under_clarification","over_clarification"]}; changed="personal_state.contacts"; mode=95
        if variant: tags += ["similar_entity_names","clarification_required"]
    else:
        # Use current-information capability availability; no arithmetic/model-capability ambiguity.
        inp["user_utterance"]=trilang(lang,("Cho tôi biết nhiệt độ ngoài trời hiện tại", "what's current outdoor temperature?", "Tell me the current outdoor temperature"))
        inp["available_local_capabilities"]=["live_weather"] if variant==0 else []
        exp={"route":"LOCAL_APP_OR_TOOL" if variant==0 else "EXTERNAL"}
        scoring={"primary":"route","secondary":["false_local","unnecessary_external"],"route_semantics_version":"v1-r1"}; changed="available_local_capabilities"; mode=96
        if variant: tags += ["local_vs_external_trap"]
    if lang=="vi_en": tags.append("code_mix")
    return inp,exp,scoring,sorted(set(tags)),mode,changed

def split_surface(text, split, lang, idx):
    if split == "calibration":
        return text
    if lang == "vi":
        wrappers = (["Giúp tôi ", "Tôi cần ", "Làm giúp việc này: "] if split=="development" else
                    ["Trong tình huống này, ", "Thực hiện yêu cầu sau: ", "Xử lý giúp tôi: ", "Làm theo ngữ cảnh này: "])
    elif lang == "en":
        wrappers = (["Please ", "I need you to ", "Could you "] if split=="development" else
                    ["In this situation, ", "Using the supplied context, ", "Handle this request: ", "Given the current context, "])
    else:
        wrappers = (["Giúp tôi ", "Please ", "Tôi cần "] if split=="development" else
                    ["Trong context này, ", "Can you ", "Xử lý request này: ", "Theo current context, "])
    w=wrappers[idx%len(wrappers)]
    if w.endswith((": ", ", ")):
        return w + text[0].lower() + text[1:] if text else w
    return w + text[0].lower() + text[1:] if text else w


def heldout_core(fam, mode, lang, inp, exp):
    # Held-out core surface forms are independently worded from calibration/development.
    P={
      "A2": {
        0:("Báo cho người bạn đời của tôi rằng tôi sẽ về muộn","text my partner rằng tối nay tôi sẽ về muộn","Tell my partner that I will be home late"),
        1:("Điện cho Tuấn","phone Tuấn giúp tôi","Phone Tuan"),
        2:("Tôi muốn gọi điện cho Mai","I need to call Mai giúp tôi","I want to phone Mai"),
        3:("Dẫn tôi đến địa chỉ nhà","route tới địa chỉ home của tôi","Take me to my home address"),
        4:("Đưa tôi tới quán cà phê quen","take me tới my regular cafe","Take me to my regular cafe"),
        5:("Dẫn tới văn phòng tôi đang làm","route tới my current office","Take me to the office where I currently work"),
      },
      "A3": {
        0:("Dùng ứng dụng điều hướng mặc định của tôi để về nhà","use my default navigation app để về home","Use my default navigation app to go home"),
        1:("Phản hồi theo ngôn ngữ tôi đặt làm mặc định","reply bằng my default language","Respond in the language I set as default"),
        2:("Máy đang ngoại tuyến; vẫn xác định đích là nhà","device is offline; destination vẫn là home","The device is offline; interpret the destination as home"),
        3:("Đưa tôi đến địa điểm làm việc mới nhất","take me tới latest work location","Take me to my latest workplace"),
        4:("Đưa tôi tới nơi tôi thường đi đầu ngày","take me tới my early-morning place","Take me to the place I usually go first thing in the morning"),
        5:("Theo ngôn ngữ của phiên chat hiện tại","use language của current chat session","Use the language of the current chat session"),
      },
      "A4": {
        0:("Chọn ứng dụng bản đồ để dẫn tôi về nhà","choose Maps để route me home","Choose the maps app to guide me home"),
        1:("Dùng ứng dụng nhắn tin báo Linh tôi đến sau 10 phút","use messaging app báo Linh 10 phút nữa tới","Use the messaging app to tell Linh I will arrive in 10 minutes"),
        2:("Tôi cần Maps để dẫn đường về nhà","I need Maps để route home","I need Maps to guide me home"),
        3:("Dùng điện thoại gọi Tuấn của dự án A","use Phone gọi Tuấn project A","Use the phone app to call Tuan from project A"),
        4:("Chọn công cụ phù hợp để tìm đường về nhà","choose the right tool để find route home","Choose the appropriate tool to find a route home"),
        5:("Mở ứng dụng quản lý lịch","open calendar-management app","Open the calendar application"),
      },
      "A5": {
        1:("Điều hướng tới nhà của tôi","navigate tới my home address","Navigate to my home"),
        2:("Đặt nhắc việc tưới cây vào 20:00","set reminder tưới cây at 20:00","Set a reminder to water the plants at 20:00"),
        3:("Thực hiện cuộc gọi tới Tuấn của dự án A","make a call tới Tuấn project A","Place a call to Tuan from project A"),
        4:("Soạn tin cho Linh","compose message cho Linh","Compose a message to Linh"),
        5:("Thêm cuộc hẹn nha sĩ ngày 12/10 lúc 09:30","add dentist appointment ngày 12/10 at 09:30","Add a dentist appointment on October 12 at 09:30"),
      },
      "A6": {
        0:("Tôi muốn gọi điện cho Mai","I want to call Mai giúp tôi","I want to phone Mai"),
        1:("Soạn tin cho Linh","compose message cho Linh","Compose a message to Linh"),
        2:("Máy không có mạng, tra cứu giá vàng hiện tại","device offline, check current gold price","The device is offline; look up the current gold price"),
        3:("Đưa tôi tới nhà","take me về home","Take me home"),
        4:("Điện cho Tuấn","phone Tuấn","Phone Tuan"),
        5:("Làm ngắn câu sau: Tôi sẽ về muộn","make this shorter: tôi sẽ về muộn","Make this shorter: I will be late"),
      },
      "A7": {
        0:("Rút câu này cho ngắn: Tôi sẽ đến muộn","make concise: tôi sẽ đến muộn","Condense this sentence: I will arrive late"),
        1:("Dùng bản đồ đưa tôi về nhà","use maps để đưa tôi về home","Use maps to take me home"),
        2:("Tra giá vàng mới nhất","check latest gold price","Get the latest gold price"),
        3:("Tôi cần gọi cho Mai","I need to call Mai","I need to phone Mai"),
        4:("Mở lịch cá nhân của tôi","open my personal Calendar","Open my personal calendar"),
        5:("Nén câu này còn một dòng: Họp dời sang 3 giờ chiều","compress to one line: Họp dời sang 3 giờ chiều","Condense to one line: The meeting moved to 3 pm"),
      },
    }
    if fam=="A1": return None
    if fam=="A5" and mode==0:
        payload=exp.get("arguments",{}).get("text")
        if payload is None: return None
        return {"vi":f"Gửi Linh nội dung: {payload}","vi_en":f"message Linh with text: {payload}","en":f"Send Linh this text: {payload}"}[lang]
    triple=P.get(fam,{}).get(mode)
    return trilang(lang,triple) if triple else None

def case_record(fam, split, local_i, lang, diff, inp, exp, scoring, tags, mode, global_i, cf_gid=None, cf_variant=None):
    variant=(local_i*7 + (0 if split=="calibration" else 2 if split=="development" else 5))%11
    if split=="test" and cf_gid is None:
        h=heldout_core(fam,mode,lang,inp,exp)
        if h: inp["user_utterance"]=add_surface_noise(h,local_i,diff,lang)
    inp["user_utterance"] = split_surface(inp["user_utterance"], split, lang, local_i if cf_gid is None else int(cf_gid.rsplit('-',1)[-1])*2)
    return {
      "case_id": f"{fam}-{ {'calibration':'C','development':'D','test':'H'}[split] }-{local_i:03d}",
      "benchmark_version": BENCHMARK_VERSION,
      "materialization_revision": MATERIALIZATION_REVISION,
      "family": fam, "split": split, "language_group": lang, "difficulty": diff,
      "adversarial_tags": tags, "counterfactual_group_id": cf_gid,
      "counterfactual_variant": cf_variant,
      "input": inp, "expected": exp, "scoring": scoring,
      "provenance": provenance(fam,split,mode,variant),
    }

def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",",":"))+"\n")

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    all_rows=[]; global_i=0
    for fam in FAMILIES:
        for split in ["calibration","development","test"]:
            langs,diffs=split_attrs(split)
            for local_i in range(SPLIT_COUNTS[split]):
                lang,diff=langs[local_i],diffs[local_i]
                if split=="test" and local_i<40:
                    pair_idx=local_i//2; variant=local_i%2; gid=f"CF-{fam}-{pair_idx:02d}"
                    inp,exp,scoring,tags,mode,_=make_counterfactual(fam,pair_idx,variant,lang,diff,global_i)
                    row=case_record(fam,split,local_i,lang,diff,inp,exp,scoring,tags,mode,global_i,gid,variant)
                else:
                    inp,exp,scoring,tags,mode=make_regular(fam,split,local_i,lang,diff,global_i)
                    row=case_record(fam,split,local_i,lang,diff,inp,exp,scoring,tags,mode,global_i)
                all_rows.append(row); global_i += 1
    for split in ["calibration","development","test"]:
        write_jsonl(ROOT/f"{split}.jsonl", [r for r in all_rows if r["split"]==split])
    schema={"benchmark_id":"track-a-capability-v1","version":BENCHMARK_VERSION,"materialization_revision":MATERIALIZATION_REVISION,
            "required_case_fields":["case_id","benchmark_version","materialization_revision","family","split","language_group","difficulty","adversarial_tags","counterfactual_group_id","input","expected","scoring","provenance"],
            "route_semantics":{"LOCAL_MODEL":"intrinsic learned local text-understanding/transformation; no external fresh knowledge or app required","LOCAL_APP_OR_TOOL":"requires an explicitly available local app/tool/live local capability","EXTERNAL":"requires non-local/fresh world capability not locally available","CLARIFY":"required information/entity choice is underdetermined"},
            "a5_text_policy":"literal_source_payload","intrinsic_model_scope":["short_text_transformation"]}
    (ROOT/"schema.json").write_text(json.dumps(schema,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    # deterministic 140-case review sample: 20/family, 6 C + 6 D + 8 H
    sample=[]
    for fam in FAMILIES:
        fr=[r for r in all_rows if r["family"]==fam]
        for split,n in [("calibration",6),("development",6),("test",8)]:
            pool=[r for r in fr if r["split"]==split]
            # evenly pick across list, ensuring test includes CF members when possible
            idxs=[]
            if split=="test": idxs=[0,1,8,9,40,55,72,91]
            else: idxs=[round(i*(len(pool)-1)/(n-1)) for i in range(n)]
            sample += [pool[i] for i in idxs[:n]]
    write_jsonl(ROOT/"human-review-sample.jsonl", sample)
    manifest={"benchmark_id":"track-a-capability-v1","version":BENCHMARK_VERSION,"materialization_revision":MATERIALIZATION_REVISION,"seed":SEED,
              "case_counts":{"calibration":280,"development":420,"test":700,"total":1400},
              "language_counts":{"vi":840,"vi_en":350,"en":210},"difficulty_counts":{"straightforward":560,"contextual":490,"adversarial":350},
              "heldout_counterfactual_cases":280,"counterfactual_groups":140,"review_sample_cases":140,
              "status":"FINAL_FROZEN_AFTER_SEMANTIC_R1_PASS",
              "hashes":{name:sha(ROOT/name) for name in ["calibration.jsonl","development.jsonl","test.jsonl","schema.json","human-review-sample.jsonl"]}}
    (ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
