
REGULAR_USER = 'A'
ADMIN_SITE_ACCESS = 'B'
MANAGE_PAYMENTS = 'C'
MANAGE_USER_COSTS = 'D'
MANAGE_COTISATION = 'E'


ROLE_DEFINITIONS = (
    dict(
        value=REGULAR_USER,
        description='Regular Association User without any admin role',
    ),
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
