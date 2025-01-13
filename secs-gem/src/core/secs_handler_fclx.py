import logging
import secsgem.common

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gemhsms.equipment_hsms import Equipment

logger = logging.getLogger("app_logger")


class HandlerFclx:
    def handle_s6f11(self, handler: 'Equipment', message: secsgem.common.Message):
        pass
        # logger.info("FCLX Handling s6f11")
        # decode = handler.settings.streams_functions.decode(message)
        # ceid = decode.CEID
        # logger.info("CEID: %s", ceid)
