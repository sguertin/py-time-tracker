from time_tracker.menu import MenuView, MenuViewEvents
from time_tracker.logging.provider import LoggingProvider
from time_tracker.settings.models import Settings

settings = Settings.load()
logging_provider = LoggingProvider(settings)
log = logging_provider.get_logger("Main")
log.info("Starting py-time-tracker...")
running = True

while running:
    menu_view = MenuView(logging_provider, settings)
    event = menu_view.run()
    log.info(f"Event: %s received!", event)
    running = event in [MenuViewEvents.SETTINGS]
