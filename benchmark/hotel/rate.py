import uuid
from uuid import uuid4
import stateflow

@stateflow.stateflow
class HotelRates:

    def get_rates(self, hotels: AllHotels):

        return


    def __key__(self):
        return str(uuid.uuid4())