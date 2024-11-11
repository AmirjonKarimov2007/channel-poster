from aiogram.contrib.fsm_storage.mongo import STATE
from aiogram.dispatcher.filters.state import State, StatesGroup


class SuperAdminStateChannel(StatesGroup):
    SUPER_ADMIN_STATE_CHANNEL = State()
    SUPER_ADMIN_STATE_CHANNELD = State()
    SUPER_ADMIN_STATE_CHANNELV = State()
    SUPER_ADMIN_STATE_CHANNELA = State()
    SUPER_ADMIN_STATE_CHANNELU = State()

class SuperAdminStateCreatePost(StatesGroup):
    SUPER_ADMIN_STATE_GET_POST_NAME = State()
    SUPER_ADMIN_STATE_GET_POST_MESSAGE_ID = State()
class SuperAdminStateCreateNomzod(StatesGroup):
    SUPER_ADMIN_STATE_GET_NOMZOD_NAME = State()
