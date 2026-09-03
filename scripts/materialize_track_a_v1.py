#!/usr/bin/env python3
import json, random
from datetime import date, timedelta
from pathlib import Path
SEED=20260904
rng=random.Random(SEED)
names_vi=["Linh","Hà","Tuấn","Minh","Lan","Hùng","Mai","Nam","Hương","Phúc","Trang","Quân"]
places_vi=["nhà","văn phòng","quán Cây","phòng gym","trường của bé","nhà mẹ","ga Hà Nội","sân bay Nội Bài"]
apps=["maps","messages","phone","calendar","notes","weather","browser","calculator"]
external_caps=["web_search","general_qa","travel_search","news_search"]
intents=["NAVIGATE","MESSAGE","CALL","REMIND","LOCAL_TRANSFORM","LOOKUP_DELEGATE","APP_ACTION","CLARIFY"]
families=[f"A{i}" for i in range(1,8)]
def quotas(n, counts):
    arr=[]
    for k,v in counts.items(): arr += [k]*v
    assert len(arr)==n
    rng.shuffle(arr)
    return arr
splits=["calibration"]*40+["development"]*60+["test"]*100
def paired_assignment(pair_counts, remaining_counts):
    pairs=[]
    for k,n_pairs in pair_counts.items():
        pairs += [k]*n_pairs
    rng.shuffle(pairs)
    pair_block=[x for x in pairs for _ in (0,1)]
    assert len(pair_block)==40
    remaining=[]
    for k,n in remaining_counts.items(): remaining += [k]*n
    rng.shuffle(remaining)
    assert len(remaining)==160
    return remaining[:100] + pair_block + remaining[100:]
def family_languages():
    return paired_assignment({"vi":12,"vi_en":5,"en":3},{"vi":96,"vi_en":40,"en":24})
def family_difficulties():
    return paired_assignment({"straightforward":8,"contextual":7,"adversarial":5},{"straightforward":64,"contextual":56,"adversarial":40})
def lang_phrase(lang, vi, mix, en): return {"vi":vi,"vi_en":mix,"en":en}[lang]
def prov(i, family):
    return {"truth_source":"rule_defined","generator":"scripts/materialize_track_a_v1.py","generator_seed":SEED,"review_status":"automated_qa_pass_human_spot_review_pending","template_id":f"{family}-T{i%25:02d}"}

def make_case(fam, i, split, lang, diff, cf_gid=None, cf_variant=None):
    base_i = i if cf_gid is None else i - (cf_variant or 0)
    context={"date_local":str(date(2026,1,1)+timedelta(days=base_i)),"time_local":f"{7+(base_i%13):02d}:{(base_i*7)%60:02d}","location":["home","office","outside"][base_i%3],"device_state":{"network":["online","offline"][base_i%2]}}
    state={"home_label":"home","home_address":"12 Nguyen Trai, Hanoi","partner":"Linh","contacts":[{"id":"c_linh","name":"Linh","relation":"partner"},{"id":"c_tuan","name":"Tuấn","relation":"coworker","project":"A"},{"id":"c_tuan2","name":"Tuấn Anh","relation":"friend"}],"preferred_navigation_app":"maps","preferred_language":"vi"}
    avail_actions=[{"id":a,"kind":a} for a in apps[:5]]
    inp={"user_utterance":"","current_context":context,"personal_state":state,"available_actions":avail_actions,"available_local_capabilities":["text_transform","calculator","device_context"],"external_capabilities":external_caps[:]}
    tags=[]; expected={}; scoring={}
    if fam=="A1":
        intent=intents[base_i%len(intents)]
        prompts={"NAVIGATE":("Chỉ đường về nhà","open Maps về nhà","Navigate home"),"MESSAGE":("Nhắn Linh là tôi về muộn","message Linh là I'm late","Message Linh that I'll be late"),"CALL":("Gọi cho Tuấn bên dự án A","call Tuấn project A","Call Tuan from project A"),"REMIND":("Nhắc tôi 8 giờ tưới cây","remind me 8 giờ tưới cây","Remind me at 8 to water plants"),"LOCAL_TRANSFORM":("Viết câu này ngắn lại: Tôi sẽ đến muộn khoảng mười phút","shorten câu này: tôi đến muộn 10 phút","Shorten this: I will arrive about ten minutes late"),"LOOKUP_DELEGATE":("Tìm giá vàng hôm nay","check gold price hôm nay","Look up today's gold price"),"APP_ACTION":("Mở ghi chú","open Notes giúp tôi","Open Notes"),"CLARIFY":("Gửi cho anh ấy nhé","send it cho anh ấy nhé","Send it to him")}
        inp["user_utterance"]=lang_phrase(lang,*prompts[intent]); expected={"intent_label":intent}; scoring={"primary":"intent_label"}
        if intent=="CLARIFY": tags += ["ambiguous_pronoun","clarification_required"]
    elif fam=="A2":
        mode=base_i%5
        if mode==0:
            inp["user_utterance"]=lang_phrase(lang,"Nhắn cho vợ là tôi về muộn","message vợ là I'm late","Message my partner that I'll be late"); expected={"entity_mentions":["vợ" if lang!="en" else "my partner"],"resolved_entity_ids":["c_linh"],"resolved_values":["Linh"],"clarification_required":False}
        elif mode==1:
            inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn bên dự án A","call Tuấn project A","Call Tuan from project A"); expected={"entity_mentions":["Tuấn" if lang!="en" else "Tuan"],"resolved_entity_ids":["c_tuan"],"resolved_values":["Tuấn"],"clarification_required":False}
        elif mode==2:
            inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn","call Tuấn","Call Tuan"); expected={"entity_mentions":["Tuấn" if lang!="en" else "Tuan"],"resolved_entity_ids":[],"resolved_values":[],"clarification_required":True}; tags += ["similar_entity_names","clarification_required"]
        elif mode==3:
            inp["user_utterance"]=lang_phrase(lang,"Chỉ đường về nhà","Maps về home","Navigate home"); expected={"entity_mentions":["nhà" if lang!="en" else "home"],"resolved_entity_ids":["home"],"resolved_values":["12 Nguyen Trai, Hanoi"],"clarification_required":False}
        else:
            state["favorite_cafe"]="quán Cây"; state["favorite_cafe_address"]="8 Phan Dinh Phung, Hanoi"; inp["user_utterance"]=lang_phrase(lang,"Chỉ đường tới quán mình hay ngồi","navigate tới favorite cafe","Navigate to my usual cafe"); expected={"entity_mentions":["quán mình hay ngồi" if lang!="en" else "my usual cafe"],"resolved_entity_ids":["favorite_cafe"],"resolved_values":["8 Phan Dinh Phung, Hanoi"],"clarification_required":False}
        scoring={"primary":"entity_set_f1","secondary":["resolved_value_accuracy"]}
    elif fam=="A3":
        mode=base_i%5
        if mode==0:
            state["preferred_navigation_app"]="maps"; context["location"]="office"; inp["user_utterance"]=lang_phrase(lang,"Về nhà bằng app quen nhé","use usual app để về home","Use my usual app to get home"); expected={"interpretation_label":"NAVIGATE_HOME_WITH_PREFERRED_APP","normalized":{"destination":"home","app":"maps"}}
        elif mode==1:
            inp["user_utterance"]=lang_phrase(lang,"Trả lời theo ngôn ngữ tôi hay dùng","reply in my usual language","Reply in my usual language"); expected={"interpretation_label":"RESPOND_VI","normalized":{"language":"vi"}}
        elif mode==2:
            context["device_state"]["network"]="offline"; inp["user_utterance"]=lang_phrase(lang,"Chỉ đường về nhà như mọi khi","route home như usual","Route me home as usual"); expected={"interpretation_label":"NAVIGATE_HOME_OFFLINE_CONSTRAINT","normalized":{"destination":"home","network":"offline"}}; tags += ["context_preference_conflict"]
        elif mode==3:
            state.update({"old_work_location":"District 1","work_location":"District 3","work_location_status":"current"}); inp["user_utterance"]=lang_phrase(lang,"Đi tới chỗ làm hiện tại","navigate current work","Navigate to my current workplace"); expected={"interpretation_label":"CURRENT_WORK_LOCATION","normalized":{"work_location":"District 3"}}; tags += ["stale_personal_fact"]
        else:
            state["morning_destination"]="gym"; context["time_local"]="07:00"; inp["user_utterance"]=lang_phrase(lang,"Đi chỗ buổi sáng","go morning place","Go to my morning place"); expected={"interpretation_label":"MORNING_DESTINATION_GYM","normalized":{"destination":"gym"}}
        scoring={"primary":"normalized_interpretation_accuracy","secondary":["counterfactual_consistency"]}
    elif fam=="A4":
        mode=base_i%5; avail=[{"id":"maps","kind":"navigation"},{"id":"messages","kind":"messaging"},{"id":"phone","kind":"calling"},{"id":"notes","kind":"notes"}]; inp["available_actions"]=avail
        if mode==0: inp["user_utterance"]=lang_phrase(lang,"Chỉ đường về nhà","open Maps về home","Navigate home"); expected={"action_id":"maps"}
        elif mode==1: inp["user_utterance"]=lang_phrase(lang,"Nhắn Linh là tôi đến sau 10 phút","message Linh 10 phút nữa","Message Linh that I'll arrive in 10 minutes"); expected={"action_id":"messages"}
        elif mode==2: inp["available_actions"]=[x for x in avail if x["id"]!="maps"]; inp["user_utterance"]=lang_phrase(lang,"Mở Maps chỉ đường về nhà","open Maps về home","Open Maps and navigate home"); expected={"action_id":"NONE"}; tags += ["unavailable_tool","unsupported_action"]
        elif mode==3: inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn","call Tuấn","Call Tuan"); expected={"action_id":"phone"}
        else: inp["available_actions"]=[{"id":"maps","kind":"navigation"},{"id":"browser","kind":"web"}]; inp["user_utterance"]=lang_phrase(lang,"Tìm đường về nhà","find route home","Find a route home"); expected={"action_id":"maps"}; tags += ["semantically_similar_tools"]
        scoring={"primary":"action_id","secondary":["unavailable_action_false_selection"]}
    elif fam=="A5":
        mode=base_i%5
        if mode==0: inp["user_utterance"]=lang_phrase(lang,"Nhắn Linh: tôi về muộn 20 phút","message Linh: I'm late 20 phút","Message Linh: I'll be 20 minutes late"); expected={"arguments":{"contact_id":"c_linh","text":"tôi về muộn 20 phút" if lang!="en" else "I'll be 20 minutes late"}}
        elif mode==1: inp["user_utterance"]=lang_phrase(lang,"Chỉ đường về nhà","navigate home","Navigate home"); expected={"arguments":{"destination":"12 Nguyen Trai, Hanoi"}}
        elif mode==2: inp["user_utterance"]=lang_phrase(lang,"Nhắc tôi lúc 20:00 tưới cây","remind me 20:00 tưới cây","Remind me at 20:00 to water plants"); expected={"arguments":{"time":"20:00","task":"tưới cây" if lang!="en" else "water plants"}}
        elif mode==3: inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn bên dự án A","call Tuấn project A","Call Tuan from project A"); expected={"arguments":{"contact_id":"c_tuan"}}
        else: inp["user_utterance"]=lang_phrase(lang,"Nhắn Linh","message Linh","Message Linh"); expected={"arguments":{"contact_id":"c_linh","text":None}}; tags += ["missing_required_argument"]
        scoring={"primary":"slot_micro_f1","secondary":["exact_record_match"]}
    elif fam=="A6":
        mode=base_i%6
        if mode in [0,1,2]:
            required=True; reason=["AMBIGUOUS_ENTITY","MISSING_ARGUMENT","CONFLICTING_CONTEXT"][mode]
            if mode==0: inp["user_utterance"]=lang_phrase(lang,"Gửi cho anh ấy","send it cho anh ấy","Send it to him"); tags += ["ambiguous_pronoun"]
            elif mode==1: inp["user_utterance"]=lang_phrase(lang,"Nhắn Linh","message Linh","Message Linh"); tags += ["missing_required_argument"]
            else: context["device_state"]["network"]="offline"; inp["user_utterance"]=lang_phrase(lang,"Dùng app online quen thuộc nhưng không dùng mạng","use usual online app but offline","Use my usual online app without network"); tags += ["context_preference_conflict"]
        else:
            required=False; reason="NONE"
            if mode==3: inp["user_utterance"]=lang_phrase(lang,"Chỉ đường về nhà","navigate home","Navigate home")
            elif mode==4: inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn bên dự án A","call Tuấn project A","Call Tuan from project A")
            else: inp["user_utterance"]=lang_phrase(lang,"Viết ngắn lại: Tôi sẽ về muộn","shorten: tôi sẽ về muộn","Shorten: I will be late")
        expected={"clarification_required":required,"clarification_reason":reason}; scoring={"primary":"clarification_required","secondary":["under_clarification","over_clarification"]}
        if required: tags += ["clarification_required"]
    elif fam=="A7":
        route=["LOCAL_MODEL","LOCAL_APP_OR_TOOL","EXTERNAL","CLARIFY"][base_i%4]
        if route=="LOCAL_MODEL": inp["user_utterance"]=lang_phrase(lang,"Viết câu này ngắn lại: Tôi sẽ đến muộn","shorten câu này: tôi đến muộn","Shorten this: I will arrive late")
        elif route=="LOCAL_APP_OR_TOOL": inp["user_utterance"]=lang_phrase(lang,"Chỉ đường về nhà","Maps về home","Navigate home")
        elif route=="EXTERNAL": inp["user_utterance"]=lang_phrase(lang,"Giá vàng hôm nay bao nhiêu?","gold price hôm nay?","What is today's gold price?"); tags += ["world_knowledge_trap"]
        else: inp["user_utterance"]=lang_phrase(lang,"Gửi cho anh ấy","send it cho anh ấy","Send it to him"); tags += ["clarification_required","ambiguous_pronoun"]
        expected={"route":route}; scoring={"primary":"route","secondary":["false_local","unnecessary_external"]}
    if lang=="vi_en": tags.append("code_mix")
    if diff=="adversarial" and not tags: tags.append(["irrelevant_personal_state","noisy_text","local_vs_external_trap"][base_i%3]); state["irrelevant_fact"]=f"distractor-{base_i}"
    if base_i%17==0: tags.append("noisy_text"); inp["user_utterance"]=inp["user_utterance"].replace(" ","  ",1)
    if cf_gid:
        tags.append("counterfactual_context")
        if fam=="A1": inp["user_utterance"]=lang_phrase(lang,"Mở nó giúp tôi","open it giúp tôi","Open it"); inp["current_context"]["foreground_reference"]="notes" if cf_variant==0 else None; expected={"intent_label":"APP_ACTION" if cf_variant==0 else "CLARIFY"}
        elif fam=="A2":
            inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn","call Tuấn","Call Tuan")
            if cf_variant==0: inp["personal_state"]["contacts"]=[{"id":"c_tuan","name":"Tuấn","relation":"coworker","project":"A"}]; expected={"entity_mentions":["Tuấn" if lang!="en" else "Tuan"],"resolved_entity_ids":["c_tuan"],"resolved_values":["Tuấn"],"clarification_required":False}
            else: expected={"entity_mentions":["Tuấn" if lang!="en" else "Tuan"],"resolved_entity_ids":[],"resolved_values":[],"clarification_required":True}
        elif fam=="A3": inp["user_utterance"]=lang_phrase(lang,"Dùng ngôn ngữ tôi đang dùng","use current language","Use my current language"); inp["current_context"]["conversation_language"]="vi" if cf_variant==0 else "en"; expected={"interpretation_label":"RESPOND_VI" if cf_variant==0 else "RESPOND_EN","normalized":{"language":"vi" if cf_variant==0 else "en"}}
        elif fam=="A4": inp["user_utterance"]=lang_phrase(lang,"Mở Maps chỉ đường về nhà","open Maps home","Open Maps and navigate home"); inp["available_actions"]=[{"id":"maps","kind":"navigation"}] if cf_variant==0 else [{"id":"browser","kind":"web"}]; expected={"action_id":"maps" if cf_variant==0 else "NONE"}; tags += [] if cf_variant==0 else ["unavailable_tool"]
        elif fam=="A5": inp["user_utterance"]=lang_phrase(lang,"Nhắn Linh nội dung vừa nói","message Linh previous text","Message Linh the text I just said"); inp["current_context"]["last_dictated_text"]="Tôi về lúc 8" if cf_variant==0 else None; expected={"arguments":{"contact_id":"c_linh","text":"Tôi về lúc 8" if cf_variant==0 else None}}; tags += [] if cf_variant==0 else ["missing_required_argument"]
        elif fam=="A6": inp["user_utterance"]=lang_phrase(lang,"Gọi Tuấn","call Tuấn","Call Tuan"); expected={"clarification_required":False,"clarification_reason":"NONE"} if cf_variant==0 else {"clarification_required":True,"clarification_reason":"AMBIGUOUS_ENTITY"}; inp["personal_state"]["contacts"]=[{"id":"c_tuan","name":"Tuấn"}] if cf_variant==0 else inp["personal_state"]["contacts"]; tags += [] if cf_variant==0 else ["similar_entity_names","clarification_required"]
        elif fam=="A7": inp["user_utterance"]=lang_phrase(lang,"Tính 18 nhân 7","calculate 18 x 7","Calculate 18 times 7"); inp["available_local_capabilities"]=["calculator"] if cf_variant==0 else []; expected={"route":"LOCAL_MODEL" if cf_variant==0 else "EXTERNAL"}
    return {"case_id":f"{fam}-{ {'calibration':'C','development':'D','test':'T'}[split]}-{i+1:04d}","benchmark_version":"1.0","family":fam,"split":split,"language_group":lang,"difficulty":diff,"adversarial_tags":sorted(set(tags)),"counterfactual_group_id":cf_gid,"input":inp,"expected":expected,"scoring":scoring,"provenance":prov(i,fam)}

def materialize(out_dir):
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True); all_cases=[]
    for fam in families:
        flangs=family_languages(); fdiffs=family_difficulties()
        for i in range(200):
            split=splits[i]; cf_gid=None; cf_variant=None
            if 100<=i<140: cf_gid=f"CF-{fam}-{((i-100)//2)+1:03d}"; cf_variant=(i-100)%2
            all_cases.append(make_case(fam,i,split,flangs[i],fdiffs[i],cf_gid,cf_variant))
    for split in ["calibration","development","test"]:
        with (out_dir/f"{split}.jsonl").open("w",encoding="utf-8",newline="\n") as f:
            for c in [x for x in all_cases if x["split"]==split]: f.write(json.dumps(c,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
    return all_cases

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="benchmarks/track-a-capability-v1")
    args=ap.parse_args(); cases=materialize(args.out); print(f"materialized {len(cases)} cases")
