from enum import IntEnum

__all__ = (
    'Stat',
    'CHARACTER_BLOODLINES',
    'EQUIP_SLOT_IDS',
    'STATPOINTS_PER_LEVEL',
    'STATPOINTS_ID_RANGE',
    'ELO_RANKS',
    'PRESTIGE_RANKS',
)


class Stat(IntEnum):
    Strength = 0
    Stamina = 1
    Dexterity = 2
    Intelligence = 3
    Wisdom = 4
    Luck = 5
    HP = 6
    MP = 7
    HPReg = 8
    MPReg = 9
    MinDmg = 10
    MaxDmg = 11
    Defense = 12
    Block = 13
    Critical = 14
    MoveSpeed = 15
    Haste = 16
    AttackSpeed = 17
    ItemFind = 18
    BagSlots = 19
    Prestige = 20
    Rating = 21
    StatPoints = 22
    SkillPoints = 23
    SkillPointsMax = 24
    GearScore = 25
    PVPLevel = 26
    Size = 27
    Invisibility = 28
    Sight = 29
    PercentIncreasedDmg = 30
    PercentIncreasedAggroGeneration = 31
    PercentMovementSpeedReduction = 32
    HealingReduction = 33

    DPS = 101
    Burst = 102
    EHP = 103
    DPSScore = 104
    TankScore = 105
    HybridScore = 106
    OverallScore = 107


CHARACTER_BLOODLINES: tuple[int, ...] = (
    Stat.Strength,
    Stat.Intelligence,
    Stat.Dexterity,
    Stat.Wisdom,
)
EQUIP_SLOT_IDS = frozenset({101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111})

STATPOINTS_PER_LEVEL = 3
STATPOINTS_ID_RANGE = 6

ELO_RANKS = (0, 1600, 1800, 2000, 2200)
PRESTIGE_RANKS = (0, 4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000, 40000, 44000, 48000)
