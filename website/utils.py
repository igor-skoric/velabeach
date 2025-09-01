from .models import Stage, LoungerType
from django.contrib.auth import get_user_model

User = get_user_model()


def create_loungers_stage_A(stage='A'):
    PREFIXES = ["I", "II", "III", "IV", "V", "VI", "VII"]
    # L - lezaljka, B - Baldahin
    lounger_types = ['L', 'B']
    positions = []
    obstacles = []
    for lounger_type in lounger_types:
        if lounger_type == 'L':
            for p in PREFIXES:
                for n in range(1, 9):
                    positions.append(f"{p}{n}")
            obstacles = []
        else:
            positions = [str(n) for n in range(1, 40)]
            obstacles = []

        try:
            stage = Stage.objects.get(name=stage)
            lounger_type = LoungerType.objects.get(name=lounger_type)
        except (Stage.DoesNotExist, LoungerType.DoesNotExist) as e:
            print(f"Greška: {e}")
            return

        created_count = 0


    print(f"Kreirano novih ležaljki: {created_count}")


def create_loungers_stage_B(stage='B'):
    PREFIXES = ["I", "II", "III", "IV", "V", "VI", "VII"]
    # L - lezaljka, B - Baldahi
    lounger_types = ['L', 'B']
    positions = []
    obstacles = []
    for lounger_type in lounger_types:
        if lounger_type == 'L':
            for p in PREFIXES:
                for n in range(1, 11):
                    positions.append(f"{p}{n}")
            obstacles = []
        else:
            positions = [str(n) for n in range(39, 101)]
            obstacles = []
        try:
            stage = Stage.objects.get(name=stage)
            lounger_type = LoungerType.objects.get(name=lounger_type)
        except (Stage.DoesNotExist, LoungerType.DoesNotExist) as e:
            print(f"Greška: {e}")
            return

        created_count = 0
        for position in positions:
            from .models import Lounger
            lounger, created = Lounger.objects.get_or_create(
                stage=stage,
                lounger_type=lounger_type,
                position=position,
                defaults={"is_obstacle": False}
            )
            if created:
                created_count += 1

    print(f"Kreirano novih ležaljki: {created_count}")


def create_loungers_stage_C(stage='C'):
    PREFIXES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    # L - lezaljka, B - Baldahi
    lounger_types = ['L']
    positions = []
    obstacles = []
    for lounger_type in lounger_types:
        if lounger_type == 'L':
            for p in PREFIXES:
                for n in range(1, 9):
                    positions.append(f"{p}{n}")
            obstacles = []

        try:
            stage = Stage.objects.get(name=stage)
            lounger_type = LoungerType.objects.get(name=lounger_type)
        except (Stage.DoesNotExist, LoungerType.DoesNotExist) as e:
            print(f"Greška: {e}")
            return

        created_count = 0
        for position in positions:
            from .models import Lounger
            lounger, created = Lounger.objects.get_or_create(
                stage=stage,
                lounger_type=lounger_type,
                position=position,
                defaults={"is_obstacle": False}
            )
            if created:
                created_count += 1

    print(f"Kreirano novih ležaljki: {created_count}")


def create_loungers_stage_D(stage='D'):
    PREFIXES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    # L - lezaljka, B - Baldahi
    lounger_types = ['L']
    positions = []
    obstacles = []
    for lounger_type in lounger_types:
        if lounger_type == 'L':
            for p in PREFIXES:
                for n in range(1, 11):
                    positions.append(f"{p}{n}")
            obstacles = []

        try:
            stage = Stage.objects.get(name=stage)
            lounger_type = LoungerType.objects.get(name=lounger_type)
        except (Stage.DoesNotExist, LoungerType.DoesNotExist) as e:
            print(f"Greška: {e}")
            return

        created_count = 0
        for position in positions:
            from .models import Lounger
            lounger, created = Lounger.objects.get_or_create(
                stage=stage,
                lounger_type=lounger_type,
                position=position,
                defaults={"is_obstacle": False}
            )
            if created:
                created_count += 1

    print(f"Kreirano novih ležaljki: {created_count}")


def check_user_role(user):
    if not user:
        return "anonymous"

    if user.is_superuser:
        return "admin"
    elif user.is_staff:
        return "moderator"
    else:
        return "user"


def count_loungers(stage_name: str = None, lounger_type: str = "L") -> int:
    """
    Vrati broj kreveta ili ležaljki za određeni stage.
    Ako stage_name nije prosleđen -> računa za sve stage-ove.

    :param stage_name: npr. "A", "B", "C", "D"
    :param lounger_type: "B" za krevete, "L" za ležaljke
    """
    from .models import Lounger
    qs = Lounger.objects.filter(
        lounger_type__name=lounger_type,
        is_obstacle=False
    )

    if stage_name:
        qs = qs.filter(stage__name=stage_name)

    return qs.count()