from aiogram import Router, Dispatcher

from . import start, sleep_survey, sleep_analysis, notifications

def register_all_handlers(dp: Dispatcher):
    main_router = Router()
    main_router.include_router(start.router)
    main_router.include_router(sleep_survey.router)
    main_router.include_router(sleep_analysis.router)
    main_router.include_router(notifications.router)

    dp.include_router(main_router)