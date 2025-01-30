class Lotinfo_:
    def __init__(self):
        self.lot_info_api = self.__LotInfoAPI()

    class __LotInfoAPI:
        def __init__(self):
            pass

        def _build_url(self):
            pass

        def __get_lot_info(self):
            pass

    def get_lot_info_api(self):
        return self.lot_info_api


l = Lotinfo_()
# print(l.get_lot_info_api())  # ใช้งานได้
# # AttributeError: 'Lotinfo_' object has no attribute '__lot_info_api'
# print(l.__lot_info_api)
# # AttributeError: type object 'Lotinfo_' has no attribute '__LotInfoAPI'
# print(l.__LotInfoAPI())

print(l.get_lot_info_api()._build_url())  # ใช้งานได้
print(l.get_lot_info_api().__get_lot_info())  # ใช้งานได้
