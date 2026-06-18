from aiogram.fsm.state import State, StatesGroup


class LeadFlowStates(StatesGroup):
    main_menu = State()
    waiting_audit_description = State()
    waiting_contact = State()
