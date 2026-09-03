#!/usr/bin/env python3
import json,re
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]/'benchmarks'/'track-a-capability-v1'
rows=[]
for n in ['calibration.jsonl','development.jsonl','test.jsonl']:
    rows += [json.loads(x) for x in open(ROOT/n,encoding='utf-8') if x.strip()]
issues=[]
def issue(sev,code,c,msg): issues.append((sev,code,c['case_id'],msg))
for c in rows:
    fam=c['family']; inp=c['input']; exp=c['expected']; u=inp['user_utterance']; ul=u.lower()
    if fam=='A1':
        label=exp['intent_label']
        if label=='CLARIFY':
            if c.get('counterfactual_group_id') is None and any(k in inp['current_context'] for k in ['foreground_reference','referent_id']):
                issue('CRITICAL','A1_CLARIFY_RESOLVED',c,'clarify truth but explicit referent context exists')
    elif fam=='A2':
        contacts=inp['personal_state'].get('contacts',[]); names=[x.get('name') for x in contacts]
        clar=exp.get('clarification_required')
        if clar:
            if 'mai' in ul and names.count('Mai') < 2: issue('CRITICAL','A2_FALSE_AMBIGUITY',c,'Mai clarify without duplicate Mai candidates')
        else:
            ids=exp.get('resolved_entity_ids',[])
            if 'tuấn' in ul or 'tuan' in ul:
                if names.count('Tuấn')!=1: issue('CRITICAL','A2_TUAN_NOT_UNIQUE',c,'exact Tuấn resolution without one exact Tuấn')
                if ids!=['c_tuan']: issue('CRITICAL','A2_TUAN_WRONG_ID',c,str(ids))
            if ids==['home'] and inp['personal_state'].get('home_address')!=exp.get('resolved_values',[None])[0]: issue('CRITICAL','A2_HOME_MISMATCH',c,'home value mismatch')
            if ids==['favorite_cafe'] and inp['personal_state'].get('favorite_cafe_address')!=exp.get('resolved_values',[None])[0]: issue('CRITICAL','A2_CAFE_MISMATCH',c,'cafe mismatch')
            if ids==['current_work_location'] and inp['personal_state'].get('current_work_location')!=exp.get('resolved_values',[None])[0]: issue('CRITICAL','A2_WORK_MISMATCH',c,'work mismatch')
    elif fam=='A3':
        norm=exp.get('normalized',{})
        if 'language' in norm:
            wanted=norm['language']
            if exp['interpretation_label'].startswith('RESPOND_'):
                if 'conversation_language' in inp['current_context']:
                    if inp['current_context']['conversation_language']!=wanted: issue('CRITICAL','A3_LANG_CONTEXT_MISMATCH',c,'conversation language mismatch')
                elif inp['personal_state'].get('preferred_language')!=wanted: issue('CRITICAL','A3_LANG_PREF_MISMATCH',c,'preferred language mismatch')
        if norm.get('app') and inp['personal_state'].get('preferred_navigation_app')!=norm['app']: issue('CRITICAL','A3_APP_MISMATCH',c,'preferred app mismatch')
        if norm.get('work_location') and inp['personal_state'].get('current_work_location')!=norm['work_location']: issue('CRITICAL','A3_WORK_MISMATCH',c,'current work mismatch')
        if norm.get('destination')=='gym' and inp['personal_state'].get('morning_destination')!='gym': issue('CRITICAL','A3_MORNING_MISMATCH',c,'morning destination mismatch')
        if norm.get('network') and inp['current_context'].get('device_state',{}).get('network')!=norm['network']: issue('CRITICAL','A3_NETWORK_MISMATCH',c,'network mismatch')
    elif fam=='A4':
        aid=exp['action_id']; avail={x['id'] for x in inp.get('available_actions',[])}
        if aid not in {'NONE','CLARIFY'} and aid not in avail: issue('CRITICAL','A4_EXPECTED_UNAVAILABLE',c,f'{aid} not available')
        if aid=='NONE' and 'maps' in ul and 'maps' in avail: issue('CRITICAL','A4_NONE_DESPITE_MAPS',c,'NONE while explicitly requested Maps is available')
    elif fam=='A5':
        args=exp.get('arguments',{}); src=c.get('scoring',{}).get('text_source')
        if src=='utterance_payload':
            text=args.get('text')
            if text is not None and str(text).lower() not in ul: issue('CRITICAL','A5_TRANSLATED_PAYLOAD',c,f'{text!r} not in source')
        if src=='current_context.last_dictated_text' and args.get('text')!=inp['current_context'].get('last_dictated_text'): issue('CRITICAL','A5_CONTEXT_TEXT_MISMATCH',c,'dictated text mismatch')
        if args.get('contact_id')=='c_tuan' and not any(x.get('id')=='c_tuan' for x in inp['personal_state'].get('contacts',[])): issue('CRITICAL','A5_CONTACT_MISSING',c,'c_tuan absent')
        if args.get('destination') and args['destination']!=inp['personal_state'].get('home_address'): issue('CRITICAL','A5_DEST_MISMATCH',c,'home address mismatch')
        if args.get('date')=='2026-10-12' and c['language_group']=='en' and 'october 12' not in ul: issue('CRITICAL','A5_EN_DATE_AMBIGUOUS',c,'English date not spelled unambiguously')
    elif fam=='A6':
        clar=exp['clarification_required']; reason=exp['clarification_reason']; contacts=inp['personal_state'].get('contacts',[]); names=[x.get('name') for x in contacts]
        if clar and reason=='AMBIGUOUS_ENTITY' and names.count('Mai')<2: issue('CRITICAL','A6_FALSE_AMBIGUITY',c,'ambiguity without duplicate Mai')
        if clar and reason=='MISSING_ARGUMENT' and not ('nhắn linh' in ul or 'message linh' in ul or 'compose message' in ul or 'compose a message' in ul or 'soạn tin' in ul): issue('MAJOR','A6_MISSING_ARG_SURFACE',c,'missing-argument case not obviously message-without-content')
        if not clar and ('gọi tuấn' in ul or 'call tuấn' in ul or 'phone tuấn' in ul or 'phone tuan' in ul):
            if names.count('Tuấn')!=1: issue('CRITICAL','A6_TUAN_AMBIGUOUS',c,'Tuấn no-clarify without unique exact name')
    elif fam=='A7':
        route=exp['route']; actions={x['id'] for x in inp.get('available_actions',[])}; caps=set(inp.get('available_local_capabilities',[]))
        if route=='LOCAL_APP_OR_TOOL':
            if ('nhà' in ul or 'home' in ul) and not ('maps' in actions): issue('CRITICAL','A7_LOCAL_NAV_NO_MAPS',c,'navigation local route without maps')
            if ('lịch' in ul or 'calendar' in ul) and 'calendar' not in actions: issue('CRITICAL','A7_LOCAL_CAL_NO_CAL',c,'calendar local route without calendar')
            if ('nhiệt độ' in ul or 'temperature' in ul) and 'live_weather' not in caps: issue('CRITICAL','A7_LOCAL_WEATHER_NO_CAP',c,'weather local route without live_weather')
        if route=='EXTERNAL':
            if ('nhiệt độ' in ul or 'temperature' in ul) and 'live_weather' in caps: issue('CRITICAL','A7_EXTERNAL_DESPITE_LOCAL_WEATHER',c,'external despite live weather')
        if route=='CLARIFY':
            names=[x.get('name') for x in inp['personal_state'].get('contacts',[])]
            if 'mai' in ul and names.count('Mai')<2: issue('CRITICAL','A7_FALSE_CLARIFY',c,'Mai clarify without duplicate names')
        if route=='LOCAL_MODEL':
            if not any(k in ul for k in ['rút','shorten','summar','tóm tắt','nén','condense','concise','compress']): issue('CRITICAL','A7_LOCAL_MODEL_OUT_OF_SCOPE',c,'not a short text transform')
            if ':' not in u: issue('CRITICAL','A7_LOCAL_MODEL_NO_PAYLOAD',c,'text transform lacks explicit payload')
summary={'status':'PASS' if not [i for i in issues if i[0] in {'CRITICAL','MAJOR'}] else 'REVISE','cases':len(rows),'issues':issues,'diversity':{}}
for fam in [f'A{i}' for i in range(1,8)]:
    cs=[c for c in rows if c['family']==fam]
    summary['diversity'][fam]={'unique_utterances':len({c['input']['user_utterance'].lower() for c in cs}),'unique_vi_en':len({c['input']['user_utterance'].lower() for c in cs if c['language_group']=='vi_en'})}
print(json.dumps(summary,ensure_ascii=False,indent=2))
