
FULL_ADMIN = 'A'
PAYMENT_MANAGER = 'B'
COST_MANAGER = 'C'
COTISATION_MANAGER = 'D'


ROLE_DEFINITIONS = (
    dict(
        value=FULL_ADMIN,
        description='Admin with full access',
    ),
    dict(
        value=PAYMENT_MANAGER,
        description='Admin role with ability to enter and/or modify members payments',
    ),
    dict(
        value=COST_MANAGER,
        description='Admin role with ability to subtract members costs',
    ),
    dict(
        value=COTISATION_MANAGER,
        description='Admin role with ability to manage a `cotisation` round',
    ),
)
