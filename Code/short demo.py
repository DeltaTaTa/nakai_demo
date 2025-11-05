from expyriment import design, control, stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK, K_SPACE, K_j, K_f, K_y, K_n
import random
import pandas as pd
import os
import itertools

# -------- Global Setting ----------
exp = design.Experiment(name="Cross-Domain Priming", background_colour=C_WHITE, foreground_colour=C_BLACK)
exp.add_data_variable_names(['session', 'trial', 'direction', 'congruency',
                             'lang_type',  'language_text',  'language_branch', 'language_coherency',  'lang_RT',  'lang_key',
                             'arith_type', 'arithmetic_text', 'arithmetic_branch', 'arithmetic_coherency', 'arith_RT', 'arith_key'])

control.set_develop_mode()
control.initialize(exp)
control.start(subject_id=random.randint(1, 999))

# ATTENTION: mac user：if path error，replace this lin with the path of stimuli.xlsx
current_path = os.path.dirname(os.path.abspath(__file__))

# Assign the hand
hand = "LEFT" if exp.subject % 2 == 1 else "RIGHT"

# Session, Trial
n_session_RS = 1    # 4
n_trial_RS = 4      # 16

n_session_FL = 1    # 2
n_block_FL = 1      # 4
n_trial_FL = 8      # 8

# Key
YES_KEY = K_y
NO_KEY = K_n
KEYS = [YES_KEY, NO_KEY]
key_map = {K_y: 'YES', K_n: 'NO'}

# Duration
FIXATION_DURATION = 800
STIMULUS_DURATION = 2000
BLANK_DURATION = 200

# Inter-trial Interval(s)
ITI_RS = [3000, 4000]     # ITI for RS session [12000, 15000]
ITI_FL = [3000, 4000]     # ITI for FL session [4500, 7500]

# Inter-block Interval(s)
IBI_FL = 15000          # IBI for FL session 15 s

""" Instructions """
INSTR_START =  f"""
In the following experiment, you will see English sentences and arithmetic expressions.

Please make a judgment for each stimulus:
- For sentences: decide whether it is semantically natural (Natural: 'y' / Unnatural: 'n').
- For arithmetics: decide whether the result is a multiple of ten (e.g. 10, 20, 30...) (Yes: 'y' / No: 'n').

Please respond as quickly and accurately as possible within the 2-second presentation period.

PLEASE press button with your {hand} hand.

Press SPACE to begin.
"""
INSTR_MID = """You have finished one session of the experiment, well done! \n Press SPACE to continue."""
INSTR_END = """Well done! You finish all!!!\n Press SPACE to quit the experiment."""
ITI_WAIT = ''
IBI_WAIT = ''

INSTRUCTION_COLOR = [102, 102, 102]

""" Stimulus """
FIXATION = stimuli.FixCross(colour=(255, 0, 0))
FIXATION.preload()

# ---- Stimulus ----
# 32 Sentence [16 LB (8√8X) + 16 RB (8√8X)], 32 Arithmetic [16 LB (8√8X) + 16 RB (8√8X)]
# √: coherence (natural/10n)
# X: incoherence (unnatural/not 10n)
stimulus_df = pd.read_excel(os.path.join(current_path,"stimuli.xlsx"))

# ---- Condition ----
# 4 RS Sessions(16 trials each):
# (1) Lang to Arith, Congruent
# (2) Lang to Arith, Incongruent
# (3) Arith to Lang, Congruent
# (4) Arith to Lang, Incongruent
# Congruent: LB - LB, RB - RB
# Incongruent: LB - RB, RB - LB
# 
# 2 Functional Localizer Sessions(32 trials each):
# test all stimulus randomly

# -------- Functions ------------
def present_instructions(text, key = K_SPACE):
    instructions = stimuli.TextScreen(text=text, text_justification=0, heading="Instructions")
    instructions.present()
    exp.keyboard.wait(key)

def derangements_RS(df):
    # generate stimuli sequence for RS sessions (illustration see ppt)
    sent_df = df[df.type=='language'].copy()
    arith_df = df[df.type=='arithmetic'].copy()
    def split_groups(df):
        return {
            'Lcoh': df[(df.branch=='LB') & (df.coherency=='coherent')].copy(),
            'Lincoh': df[(df.branch=='LB') & (df.coherency=='incoherent')].copy(),
            'Rcoh': df[(df.branch=='RB') & (df.coherency=='coherent')].copy(),
            'Rincoh': df[(df.branch=='RB') & (df.coherency=='incoherent')].copy(),
        }
    sent_groups = split_groups(sent_df)
    arith_groups = split_groups(arith_df)

    # -------------------
    # Lang -> Arith 
    # shuffle arith group order
    s_group_order = list(sent_groups.keys())
    a_group_order = list(arith_groups.keys())
    random.shuffle(a_group_order)

    pairs_LangArith = []
    a_available = {k: list(v.to_dict('records')) for k,v in arith_groups.items()}
    for s_group_name, s_group in sent_groups.items():
        s_list = s_group.to_dict('records')
        for i, s in enumerate(s_list):
            a_group_name = a_group_order[(i // 2) % len(a_group_order)]
            # print(a_group_name)
            
            if a_available[a_group_name]:
                a = a_available[a_group_name].pop(0)
                pairs_LangArith.append({
                    'direction': 'Lang->Arith',
                    'language_text': s['text'],
                    'language_branch': s['branch'],
                    'language_coherency': s['coherency'],
                    'arithmetic_text': a['text'],
                    'arithmetic_branch': a['branch'],
                    'arithmetic_coherency': a['coherency']})
            # print(f"{s['text']} ==== {a['text']}")

    # -------------------
    # Arith -> Lang 
    pairs_ArithSent = []
    # derange group order
    a_group_order_copy = a_group_order.copy()
    while True:
        random.shuffle(a_group_order)
        if a_group_order != a_group_order_copy:
            break

    s_available = {k: list(v.to_dict('records')) for k,v in sent_groups.items()}
    for a_group_name in a_group_order:
        a_group = arith_groups[a_group_name]
        a_list = a_group.to_dict('records')
        
        for i, a in enumerate(a_list):
            s_group_name = s_group_order[(i // 2) % len(s_group_order)]
            if s_available[s_group_name]:
                s = s_available[s_group_name].pop(0)
                pairs_ArithSent.append({
                    'direction': 'Arith->Lang',
                    'arithmetic_text': a['text'],
                    'arithmetic_branch': a['branch'],
                    'arithmetic_coherency': a['coherency'],
                    'language_text': s['text'],
                    'language_branch': s['branch'],
                    'language_coherency': s['coherency']})
            # print(f"{a['text']} ==== {s['text']}")
                
    pairs_df = pd.DataFrame(pairs_LangArith + pairs_ArithSent)
    pairs_df = pairs_df.sample(frac=1, random_state=42).reset_index(drop=True)
    return pairs_df

def derangements_FL(df):
    # shuffle stimli for Functional Localizer Sessions 
    # df_shuffled = df.sample(frac=1).reset_index(drop=True)
    sess_tag = ['coherent', 'incoherent']
    random.shuffle(sess_tag)

    sessions = {}
    for coh in sess_tag:
        # Step 1: select one coherency subset
        df_sub = df[df['coherency'] == coh].reset_index(drop=True)

        # Step 2: divide into 4 subgroups by (type, branch)
        conditions = [
            ('language', 'LB'),
            ('language', 'RB'),
            ('arithmetic', 'LB'),
            ('arithmetic', 'RB')
        ]
        
        groups = []
        for t, b in conditions:
            group = (
                df_sub[(df_sub['type'] == t) & (df_sub['branch'] == b)]
                .sample(frac=1, random_state=None)  # shuffle within group
                .reset_index(drop=True)
            )
            groups.append(group)
        
        # Step 3: shuffle group order
        random.shuffle(groups)

        # Step 4: concatenate all groups for this session
        session_df = pd.concat(groups, ignore_index=True)

        # Save session
        sessions[coh] = session_df

    df_shuffled = pd.concat([sessions[sess_tag[0]], sessions[sess_tag[1]]], ignore_index=True)

    return df_shuffled

def timed_draw(*stims):
    t0 = exp.clock.time
    exp.screen.clear()
    for stim in stims:
        stim.present(clear=False, update=False)
    exp.screen.update()
    t1 = exp.clock.time
    return t1 - t0

def present_for(*stims, t=1000):
    dt = timed_draw(*stims)
    exp.clock.wait(t - dt)

def present_for_wait_key(*stims, t=1000):
    # check keyboard while present stimuli
    dt = timed_draw(*stims)
    t_start = exp.clock.time
    exp.keyboard.clear()
    key = None
    rt = None
    responded = False

    while exp.clock.time - t_start < t:
        k = exp.keyboard.check(KEYS)
        if (not responded) and (k is not None):
            key = k
            rt = exp.clock.time - t_start
            responded = True
        exp.clock.wait(1)

    return key, rt

def present_blank(t=200):
    # present a blank interval
    exp.screen.clear()
    exp.screen.update()
    exp.clock.wait(t)

def present_ITI(iti_win, text = ''):
    # prensent the inter-trial interval
    iti = random.randint(iti_win[0], iti_win[1]) 
    wait_text = stimuli.TextLine(text=text, text_colour=INSTRUCTION_COLOR)
    wait_text.present()
    exp.clock.wait(iti)

def present_IBI(t, text = ''):
    # prensent the inter-trial interval
    wait_text = stimuli.TextLine(text=text, text_colour=INSTRUCTION_COLOR)
    wait_text.present()
    exp.clock.wait(t)

""" Trial """
def run_trial_RS(stims, session = '', trial = ''):
    """ --- 4 RS Sessions ---
    a small red cross 800ms
    A-expression 2000ms
    blank 200ms
    sentence 2000ms
    ITI: RS Sessions 12000-15000ms
    """ 
    direction = stims['direction']
    language_text = stims['language_text']
    language_branch = stims['language_branch']
    language_coherency = stims['language_coherency']
    arithmetic_text = stims['arithmetic_text']
    arithmetic_branch = stims['arithmetic_branch']
    arithmetic_coherency =stims['arithmetic_coherency']

    if direction == "Lang->Arith":
        stim1_text = language_text
        stim2_text = arithmetic_text
    else:  # Arith->Lang
        stim1_text = arithmetic_text
        stim2_text = language_text

    stim1 = stimuli.TextLine(text=stim1_text)
    stim1.preload()
    stim2 = stimuli.TextLine(text=stim2_text)
    stim2.preload()
    
    # fixation
    present_for(FIXATION, t=FIXATION_DURATION)
    # stimulus 1
    key_1, rt_1 = present_for_wait_key(stim1, t=STIMULUS_DURATION)
    # blank
    present_blank(t=BLANK_DURATION)
    # stimulus 2
    key_2, rt_2 = present_for_wait_key(stim2, t=STIMULUS_DURATION)

    if direction == 'Lang->Arith':
        lang_RT = rt_1
        arith_RT = rt_2
        lang_key = 'none'
        arith_key = 'none'
        if key_1:
            lang_key = key_map[key_1]
        if key_2:
            arith_key = key_map[key_2]
    else: # 'AL'
        arith_RT = rt_1
        lang_RT = rt_2
        lang_key = 'none'
        arith_key = 'none'
        if key_1:
            arith_key = key_map[key_1]
        if key_2:
            lang_key = key_map[key_2]

    congruency = stims['language_branch'] == stims['arithmetic_branch']

    exp.data.add([session, trial, direction, congruency,
                  'language', language_text, language_branch, language_coherency, lang_RT, lang_key,
                  'arithmetic', arithmetic_text, arithmetic_branch, arithmetic_coherency, arith_RT, arith_key])
    # ITI
    present_ITI(ITI_RS, text = ITI_WAIT)

def run_trial_FL(stims, session = '', trial = '', direction = '', coherency = ''):
    """ --- 2 Functional Localizer Sessions ---
    a small red 800ms
    A-expression/Sentence 2000ms
    ITI: RS Sessions 4500-7500ms
    """
    type = stims['type']
    text = stims['text']
    branch = stims['branch']
    coherency = stims['coherency']
    
    stim = stimuli.TextLine(text=text)
    stim.preload()

    # fixation
    present_for(FIXATION, t=FIXATION_DURATION)
    # stimulus
    key, rt = present_for_wait_key(stim, t=STIMULUS_DURATION)

    lang_type = lang_text = lang_branch = lang_coh = lang_RT = lang_key = \
    arith_type = arith_text = arith_branch = arith_coh = arith_RT = arith_key = 'none'

    if type == 'language':
        lang_type = type
        lang_text = text
        lang_branch = branch
        lang_coh = coherency
        lang_RT = rt
        if key:
            lang_key = key_map[key]
    else: # 'arithmetic'
        arith_type = type
        arith_text = text
        arith_branch = branch
        arith_coh = coherency
        arith_RT = rt
        if key:
            arith_key = key_map[key]

    exp.data.add([session, trial_id, 'none', 'none',
                  lang_type, lang_text, lang_branch, lang_coh, lang_RT, lang_key,
                  arith_type, arith_text, arith_branch, arith_coh, arith_RT, arith_key])
    
    # ITI 
    present_ITI(ITI_FL)

# -------- Main ------------

# generate stimuli sequence
stim_RS = derangements_RS(stimulus_df)
stim_FL = derangements_FL(stimulus_df)

# instruction
present_instructions(INSTR_START)

# 4 RS sessions
row = 0
for sess_id in range(1, n_session_RS + 1):
    instructions = stimuli.TextLine(text=f'Session {sess_id} starts soon. Press SPACE to continue.', text_colour=INSTRUCTION_COLOR)
    instructions.present()
    exp.keyboard.wait(K_SPACE)
    for trial_id in range(1, n_trial_RS + 1):
        run_trial_RS(stim_RS.iloc[row], session = f"RS{sess_id}", trial = trial_id)
        row = row + 1

    present_instructions(INSTR_MID)

# 2 functional localizer sessions
row = 0
for sess_id in range(1, n_session_FL + 1):
    instructions = stimuli.TextLine(text=f'Session {n_session_RS+sess_id} starts soon. Press SPACE to continue.', text_colour=INSTRUCTION_COLOR)
    instructions.present()
    exp.keyboard.wait(K_SPACE)
    for block in range(1, n_block_FL+1):
        for trial_id in range(1, n_trial_FL + 1):
            run_trial_FL(stim_FL.iloc[row], session = f"FL{sess_id}", trial = trial_id)
            # print(stim_FL.iloc[row]['text'])
            row = row + 1

        present_IBI(IBI_FL, text = IBI_WAIT)

    if not sess_id == n_session_FL:
        present_instructions(INSTR_MID)

present_instructions(INSTR_END)

control.end()

# ---------------------------------------
# print collected data
# ---------------------------------------
from expyriment.misc.data_preprocessing import read_datafile
import pandas as pd

# read .xpd 
data, variables, subject_info, comments = read_datafile(f"data/short demo_{exp.subject}.xpd")
df = pd.DataFrame(data, columns=variables)
print(df)

# write into xlsx
output_path = f"data/experiment_{exp.subject}.xlsx"
df.to_excel(output_path, index=False)

print(f"DataFrame saved at {output_path}.")


