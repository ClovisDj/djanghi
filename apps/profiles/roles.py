
ADMIN_SITE_ACCESS = 'A'
MANAGE_PAYMENTS = 'B'
MANAGE_USER_COSTS = 'C'
MANAGE_COTISATION = 'D'

FULL_ADMIN_DEFINITION = (
    ADMIN_SITE_ACCESS,
    MANAGE_PAYMENTS,
    MANAGE_USER_COSTS,
    MANAGE_COTISATION
)

ROLE_DEFINITIONS = (
    dict(
        value=ADMIN_SITE_ACCESS,
        description='Basic Admin role with read only access to his/her association admin pages',
    ),
    dict(
        value=MANAGE_PAYMENTS,
        description='Admin role with ability to enter and/or modify members payments',
    ),
    dict(
        value=MANAGE_USER_COSTS,
        description='Admin role with ability to subtract members costs',
    ),
    dict(
        value=MANAGE_COTISATION,
        description='Admin role with ability to manage a `cotisation` round',
    ),
)
