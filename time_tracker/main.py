from time_tracker.constants import CLOSE_EVENTS

from time_tracker.factories.dependencies import DependencyFactory

view_factory, log_provider = DependencyFactory.make_dependencies()
log = log_provider.get_logger("Main")
log.info("Starting py-time-tracker...")
running = True

while running:
    menu_view = view_factory.make_menu_view()
    event = menu_view.run(close=True)
    log.info(f"Event: %s received!", event)
    running = event not in CLOSE_EVENTS
