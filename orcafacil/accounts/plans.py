# ==============================
# REGRAS POR PLANO (Helper)
# ==============================

PLAN_FEATURES = {
    'free': {
        'can_save_budgets': False,
        'can_save_clients': False,
        'can_upload_logo': False,
        'can_add_footer': False,
        'show_ads': True,
    },
    'pro': {
        'can_save_budgets': True,
        'can_save_clients': True,
        'can_upload_logo': True,
        'can_add_footer': False,
        'show_ads': True,
    },
    'master': {
        'can_save_budgets': True,
        'can_save_clients': True,
        'can_upload_logo': True,
        'can_add_footer': True,
        'show_ads': False,
    }
}
