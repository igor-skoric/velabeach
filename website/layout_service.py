"""Gradi layout mreže iz baze (jedan izvor istine za prikaz)."""

from django.db import transaction

from .grid_utils import to_roman
from .models import Lounger, LoungerSection, Stage
from .stage_seasons import ROW_PRICES, SECTION_META, STAGE_A_SEASON, STAGE_SEASONS

STATUS_DISPLAY = {
    'available': 'Dostupno',
    'unavailable': 'Zauzeto',
    'reserved': 'Rezervisano',
    'signature': 'Potpis',
}


def obstacle_position(grid_section: str, sort_order: int) -> str:
    return f'#{grid_section}-{sort_order}'


def _lounger_to_cell(lounger: Lounger) -> dict:
    base = {
        'grid_row': lounger.grid_row,
        'grid_col': lounger.grid_col,
        'lounger_id': lounger.id,
    }
    if lounger.is_obstacle:
        return {**base, 'isObstacle': True, 'label': 'X', 'price': 0}

    return {
        **base,
        'isObstacle': False,
        'label': lounger.position,
        'price': lounger.default_price,
        'status': 'available',
        'status_display': STATUS_DISPLAY['available'],
        'reservation': None,
    }


def build_section_from_model(section: LoungerSection) -> dict:
    loungers = list(
        section.loungers.filter(is_active=True).order_by('grid_row', 'grid_col', 'sort_order')
    )
    if not loungers:
        return {
            'cols': section.cols,
            'max_row': 0,
            'title': section.title,
            'explicit_grid': True,
            'cells': [],
        }

    min_row = min(l.grid_row for l in loungers)
    cells = []
    for lounger in loungers:
        cell = _lounger_to_cell(lounger)
        cell['grid_row'] = lounger.grid_row - min_row + 1
        cells.append(cell)

    return {
        'cols': section.cols,
        'max_row': max(c['grid_row'] for c in cells),
        'title': section.title,
        'explicit_grid': True,
        'cells': cells,
    }


def build_stage_layout(stage_name: str) -> dict | None:
    stage = Stage.objects.filter(name=stage_name).prefetch_related('sections').first()
    if not stage:
        return None

    sections = {}
    for sec in stage.sections.all().order_by('display_order'):
        if sec.loungers.filter(is_active=True).exists():
            sections[sec.code] = build_section_from_model(sec)

    return {
        'symbol': stage_name,
        'name': f'Reon {stage_name}',
        'sections': sections,
        'from_database': bool(sections),
    }


def _append_obstacle_slot(slots, sort_order, grid_section, row, col):
    slots.append({
        'sort_order': sort_order,
        'grid_row': row,
        'grid_col': col,
        'is_obstacle': True,
        'position': obstacle_position(grid_section, sort_order),
        'default_price': 0,
    })


def generate_roman_rows_slots(section_code: str, config: dict) -> list:
    cols = config['cols']
    obstacles = {tuple(o) for o in config.get('obstacles', [])}
    row_prices = {r[0]: r[1] for r in config['rows']}
    slots = []
    sort_order = 0

    for row_num, (row_letter, price) in enumerate(config['rows'], start=1):
        for col in range(1, cols + 1):
            if (row_num, col) in obstacles:
                _append_obstacle_slot(slots, sort_order, section_code, row_num, col)
            else:
                slots.append({
                    'sort_order': sort_order,
                    'grid_row': row_num,
                    'grid_col': col,
                    'is_obstacle': False,
                    'position': f'{row_letter}{col}',
                    'default_price': price,
                })
            sort_order += 1
    return slots


def generate_roman_flow_slots(section_code: str, config: dict) -> list:
    """
    Oznake I1, II3, VIII1… (flow_start_index samo za rimski red u labeli).
    grid_row/grid_col su lokalni za sekciju (1, 2, 3…) da 2. blok ne visi ispod praznih redova.
    """
    cols = config['cols']
    total = config['flow_total']
    obstacles = set(config.get('flow_obstacles', []))
    label_index = config.get('flow_start_index', 0)
    slots = []
    sort_order = 0
    slot_index = 0

    for flow_i in range(total + len(obstacles)):
        grid_row = slot_index // cols + 1
        grid_col = slot_index % cols + 1
        label_row = label_index // cols + 1
        label_col = label_index % cols + 1

        if flow_i in obstacles:
            _append_obstacle_slot(slots, sort_order, section_code, grid_row, grid_col)
        else:
            row_letter = to_roman(label_row)
            slots.append({
                'sort_order': sort_order,
                'grid_row': grid_row,
                'grid_col': grid_col,
                'is_obstacle': False,
                'position': f'{row_letter}{label_col}',
                'default_price': ROW_PRICES.get(row_letter, 15),
            })
            label_index += 1
        sort_order += 1
        slot_index += 1
    return slots


def generate_numbered_slots(section_code: str, config: dict) -> list:
    """Baldahini sa eksplicitnim (red, kolona) preprekama — npr. reon A."""
    cols = config['cols']
    price = config['price']
    count = config['count']
    start = config['start_number']
    obstacles = {tuple(o) for o in config.get('obstacles', [])}
    slots = []
    sort_order = 0
    row = 1
    col = 1
    number = start
    placed = 0
    limit = count + len(obstacles) + cols * 3

    while placed < limit and number < start + count:
        if (row, col) in obstacles:
            _append_obstacle_slot(slots, sort_order, section_code, row, col)
            placed += 1
        else:
            slots.append({
                'sort_order': sort_order,
                'grid_row': row,
                'grid_col': col,
                'is_obstacle': False,
                'position': str(number),
                'default_price': price,
            })
            number += 1
            placed += 1

        sort_order += 1
        col += 1
        if col > cols:
            col = 1
            row += 1

    return slots


def generate_numbered_flow_slots(section_code: str, config: dict) -> list:
    """Kao stari app.js za baldahine / chair2 — currentIndex za mrežu."""
    cols = config['cols']
    price = config['price']
    count = config['count']
    start = config['start_number']
    obstacles = set(config.get('flow_obstacles', []))
    slots = []
    sort_order = 0
    current_index = 0
    current_number = start

    for flow_i in range(count + len(obstacles)):
        row = current_index // cols + 1
        col = current_index % cols + 1
        if flow_i in obstacles:
            _append_obstacle_slot(slots, sort_order, section_code, row, col)
        else:
            slots.append({
                'sort_order': sort_order,
                'grid_row': row,
                'grid_col': col,
                'is_obstacle': False,
                'position': str(current_number),
                'default_price': price,
            })
            current_number += 1
        sort_order += 1
        current_index += 1
    return slots


def generate_section_slots(section_code: str, config: dict) -> list:
    if 'rows' in config:
        return generate_roman_rows_slots(section_code, config)
    if 'flow_total' in config:
        return generate_roman_flow_slots(section_code, config)
    if 'flow_obstacles' in config and 'start_number' in config:
        return generate_numbered_flow_slots(section_code, config)
    if 'start_number' in config:
        return generate_numbered_slots(section_code, config)
    raise ValueError(f'Nepoznat format sekcije {section_code}: {config}')


def _reserved_lounger_ids(stage):
    from .models import Reservation

    return set(
        Reservation.objects.filter(lounger__stage=stage).values_list('lounger_id', flat=True)
    )


def _clear_stage_orphans(stage):
    reserved_ids = _reserved_lounger_ids(stage)
    return Lounger.objects.filter(stage=stage).exclude(id__in=reserved_ids).delete()[0]


def _upsert_lounger_slot(stage, section, lounger_type, slot, reserved_ids) -> bool:
    """
    Upis jednog slota. Ako postoji rezervacija na staroj ćeliji, pomeri taj zapis na novu poziciju.
    Vraća True ako je kreiran novi red, False ako je ažuriran postojeći.
    """
    lookup = {
        'section': section,
        'grid_row': slot['grid_row'],
        'grid_col': slot['grid_col'],
    }
    defaults = {
        'stage': stage,
        'grid_section': section.code,
        'lounger_type': lounger_type,
        'sort_order': slot['sort_order'],
        'position': slot['position'],
        'is_obstacle': slot['is_obstacle'],
        'default_price': slot['default_price'],
        'is_active': True,
    }

    existing_cell = Lounger.objects.filter(**lookup).first()
    if existing_cell:
        for key, value in defaults.items():
            setattr(existing_cell, key, value)
        existing_cell.save()
        return False

    if slot['position'] and not slot['is_obstacle']:
        by_position = (
            Lounger.objects.filter(
                stage=stage,
                lounger_type=lounger_type,
                position=slot['position'],
                is_obstacle=False,
            )
            .order_by('pk')
            .first()
        )
        if by_position:
            for key, value in defaults.items():
                setattr(by_position, key, value)
            by_position.section = section
            by_position.grid_row = slot['grid_row']
            by_position.grid_col = slot['grid_col']
            by_position.save()
            Lounger.objects.filter(
                stage=stage,
                lounger_type=lounger_type,
                position=slot['position'],
                is_obstacle=False,
            ).exclude(pk=by_position.pk).exclude(id__in=reserved_ids).delete()
            return False

    Lounger.objects.filter(**lookup).exclude(id__in=reserved_ids).delete()
    Lounger.objects.create(**defaults, **lookup)
    return True


def sync_stage_layout(stage_name: str, season_config: dict | None = None, verbose: bool = True) -> dict:
    from .models import LoungerType, Reservation

    stage_name = stage_name.upper()
    season_config = season_config or STAGE_SEASONS.get(stage_name)
    if not season_config:
        raise ValueError(f'Nema šablona za reon {stage_name}')

    stage, _ = Stage.objects.get_or_create(name=stage_name)
    type_l, _ = LoungerType.objects.get_or_create(name='L')
    type_b, _ = LoungerType.objects.get_or_create(name='B')
    types = {'L': type_l, 'B': type_b}

    created = updated = 0
    reserved_ids = _reserved_lounger_ids(stage)

    with transaction.atomic():
        removed = _clear_stage_orphans(stage)
        reserved_ids = _reserved_lounger_ids(stage)
        if verbose and removed:
            print(f'Reon {stage_name}: uklonjeno {removed} starih slotova (bez rezervacija).')

        for section_code, sec_cfg in season_config.items():
            meta = SECTION_META[section_code]
            lounger_type = types[meta['lounger_type']]

            display_order = meta['display_order']
            if section_code == 'bed' and 'chair2' in season_config:
                display_order = 20

            section, _ = LoungerSection.objects.update_or_create(
                stage=stage,
                code=section_code,
                defaults={
                    'title': meta['title'],
                    'lounger_type': lounger_type,
                    'cols': sec_cfg['cols'],
                    'display_order': display_order,
                },
            )
            section.cols = sec_cfg['cols']
            section.save(update_fields=['cols'])

            slots = generate_section_slots(section_code, sec_cfg)
            if verbose:
                print(f'  {section_code}: {len(slots)} slotova, cols={sec_cfg["cols"]}')

            for slot in slots:
                if _upsert_lounger_slot(stage, section, lounger_type, slot, reserved_ids):
                    created += 1
                else:
                    updated += 1

    if verbose:
        print(f'Reon {stage_name}: kreirano {created}, ažurirano {updated}.')

    return {'created': created, 'updated': updated, 'stage': stage_name}


def sync_stage_a_layout(verbose: bool = True) -> dict:
    return sync_stage_layout('A', STAGE_A_SEASON, verbose=verbose)


def sync_stage_b_layout(verbose: bool = True) -> dict:
    return sync_stage_layout('B', verbose=verbose)


def sync_stage_c_layout(verbose: bool = True) -> dict:
    return sync_stage_layout('C', verbose=verbose)


def sync_stage_d_layout(verbose: bool = True) -> dict:
    return sync_stage_layout('D', verbose=verbose)


def sync_all_stages_layout(verbose: bool = True) -> dict:
    totals = {'created': 0, 'updated': 0, 'stages': []}
    for name in ('A', 'B', 'C', 'D'):
        result = sync_stage_layout(name, verbose=verbose)
        totals['created'] += result['created']
        totals['updated'] += result['updated']
        totals['stages'].append(result)
    return totals
