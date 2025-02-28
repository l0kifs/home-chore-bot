# from typing import Any


# logging_config: dict[str, Any] = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "simple_formatter": {
#             "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
#         },
#         "colored_formatter": {
#             "()": "colorlog.ColoredFormatter",
#             "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
#             "log_colors": {
#                 "DEBUG": "cyan",
#                 "INFO": "green",
#                 "WARNING": "yellow",
#                 "ERROR": "red",
#                 "CRITICAL": "bold_red",
#             }
#         },
#     },
#     "handlers": {
#         "console_handler": {
#             "class": "logging.StreamHandler",
#             "formatter": "colored_formatter"
#         }
#     },
#     "loggers": {
#         "root": {
#             "level": "INFO",
#             "handlers": ["console_handler"]
#         },
#         "httpx": {
#             "level": "WARNING",
#             "handlers": ["console_handler"]
#         },
#         "apscheduler.scheduler": {
#             "level": "WARNING",
#             "handlers": ["console_handler"]
#         },
#         "telegram.ext.Application": {
#             "level": "WARNING",
#             "handlers": ["console_handler"]
#         },
#     }
# }