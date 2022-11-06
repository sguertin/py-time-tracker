from time_tracker.views.menu import MenuView
from time_tracker.models.menu import MenuViewEvents
from time_tracker.providers.logging import LoggingProvider
from time_tracker.models.settings import Settings

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
