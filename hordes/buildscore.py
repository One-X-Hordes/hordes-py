from __future__ import annotations

import math
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .stats import Stats
    from .types.character import ClassId

    class Buildscore(TypedDict):
        dps: float
        burst: float
        ehp: float
        dps_score: float
        tank_score: float
        hybrid_score: float
        overall_score: float


def get_buildscore(stats: Stats, class_id: ClassId) -> Buildscore:
    hp = stats[6]
    defense = stats[12]
    block = min(stats[13] / 10, 100)
    max_dmg = stats[11]
    min_dmg = min(stats[10], max_dmg)
    crit = min(stats[14] / 10, 100)
    haste = stats[16] / 10

    block_multiplier = (0.6, 0.45, 0.45, 0.45)

    avgdmg = (min_dmg + max_dmg) / 2
    defred = (1 - math.exp(-defense * 0.0022)) * 0.87
    blockvalue = 1 - block / 100 * block_multiplier[class_id]

    dps = avgdmg * (1 + crit / 100) * (1 + haste / 100)
    burst = avgdmg * (1 + crit / 100)
    ehp = hp / ((1 - defred) * blockvalue)
    dmgred = defred + (((block / 100) * block_multiplier[class_id]))
    hpvalue = 1 / (1 - (1 - (1 - defred) * blockvalue))

    if class_id == 0:
        dps_score = (math.log(ehp, 5) + math.log(dps, 2) + math.log(burst, 2)) / 3
        tank_score = (math.log(ehp, 2) + math.log(dmgred * 100, 2) + math.log(haste, 6)) / 3
        hybrid_score = (math.log(ehp, 5) + math.log(dps, 4) + math.log(burst, 5) + math.log(dmgred * 100, 5)) / 4
        overall_score = (dps_score + tank_score / 3 + hybrid_score) * 210 / 3
    elif class_id == 1:
        burst = avgdmg * ((1 + crit / 100) * 0.8 + (1 + haste / 100) * 0.3)
        dps_score = math.log((burst + dps) / 2, 2)
        tank_score = (math.log(ehp, 2.5) + math.log(burst, 6) + math.log(dps, 6)) / 3
        hybrid_score = (math.log(ehp, 5) + math.log(burst, 5) + math.log(dps, 4)) / 3
        overall_score = (dps_score / 3 + tank_score + hybrid_score) * 225 / 3
    elif class_id == 2:
        dps_score = (math.log(burst, 2) + math.log(dps, 2)) / 2
        tank_score = (math.log(ehp, 2.5) + math.log(burst, 6) + math.log(dps, 6)) / 3
        hybrid_score = (math.log(ehp, 5) + math.log(burst, 5) + math.log(dps, 4)) / 3
        overall_score = (dps_score / 3 + tank_score + hybrid_score) * 226 / 3
    elif class_id == 3:
        dps_score = (math.log(dps, 2) + math.log(burst, 2) + math.log(ehp, 10)) / 3
        tank_score = (
            math.log(dps, 10) + math.log(burst, 11) + math.log(ehp, 2) + math.log(hpvalue * 60, 7) + math.log(haste * 8, 16)
        ) / 5
        hybrid_score = (
            math.log(dps, 3) + math.log(burst, 4) + math.log(ehp, 6) + math.log(hpvalue * 50, 10) + math.log(haste * 8, 9)
        ) / 5
        overall_score = (dps_score / 1.75 + tank_score + hybrid_score) * 235 / 3

    return {
        'dps': dps,
        'burst': burst,
        'ehp': ehp,
        'dps_score': dps_score,
        'tank_score': tank_score,
        'hybrid_score': hybrid_score,
        'overall_score': overall_score,
    }
