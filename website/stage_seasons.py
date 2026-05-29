"""
Šabloni mreže po reonima — uredi ovde, pa: python manage.py sync_loungers_stage_X
"""

# Cene po rimskom redu (ležaljke) — zajednički podrazumevano
ROW_PRICES = {
    'I': 25,
    'II': 25,
    'III': 20,
    'IV': 20,
    'V': 15,
    'VI': 15,
    'VII': 15,
    'VIII': 15,
    'IX': 15,
    'X': 15,
    'XI': 15,
}

STAGE_A_SEASON = {
    'chair': {
        'cols': 8,
        'rows': [
            ('I', 25),
            ('II', 25),
            ('III', 20),
            ('IV', 20),
            ('V', 15),
            ('VI', 15),
            ('VII', 15),
        ],
        'obstacles': [(7, 7)],
    },
    'bed': {
        'cols': 9,
        'start_number': 1,
        'count': 45,
        'price': 20,
        'obstacles': [],
    },
}

# 7 redova × 10 kolona = 70 ležaljki; baldahini 40–100
STAGE_B_SEASON = {
    'chair': {
        'cols': 10,
        'rows': [
            ('I', 25),
            ('II', 25),
            ('III', 20),
            ('IV', 20),
            ('V', 15),
            ('VI', 15),
            ('VII', 15),
        ],
        'obstacles': [],
    },
    'bed': {
        'cols': 11,
        'start_number': 46,
        'count': 55,
        'price': 20,
        'flow_obstacles': [9, 10],
    },
}

# Dva bloka ležaljki; drugi blok nastavlja rimske oznake (VIII1, VIII2, …)
STAGE_C_SEASON = {
    'chair': {
        'cols': 8,
        'flow_total': 55,
        'flow_obstacles': [55],
    },
    'chair2': {
        'cols': 9,
        'flow_total': 32,
        'flow_start_index': 63,
        'flow_obstacles': [8, 17, 26],
    },
}

STAGE_D_SEASON = {
    'chair': {
        'cols': 11,
        'flow_total': 77,
        'flow_obstacles': [],
    },
    'chair2': {
        'cols': 8,
        'flow_total': 24,
        'flow_start_index': 56,
        'flow_obstacles': [],
    },
}

STAGE_SEASONS = {
    'A': STAGE_A_SEASON,
    'B': STAGE_B_SEASON,
    'C': STAGE_C_SEASON,
    'D': STAGE_D_SEASON,
}

SECTION_META = {
    'chair': {'title': 'Ležaljke', 'lounger_type': 'L', 'display_order': 0},
    'chair2': {'title': 'Ležaljke (nastavak)', 'lounger_type': 'L', 'display_order': 1},
    'bed': {'title': 'Baldahini', 'lounger_type': 'B', 'display_order': 10},
}

# display_order: chair=0, chair2=1, bed=10 da bed bude posle oba chair bloka
