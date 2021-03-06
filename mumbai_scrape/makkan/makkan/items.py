from scrapy.item import Item,Field


class Website(Item):
    carpet_area = Field()
    updated_date = Field() 
    management_by_landlord = Field()
    areacode = Field()
    mobile_lister = Field()
    google_place_id = Field()
    immediate_possession = Field()
    age = Field()
    address = Field()
    price_on_req = Field()
    sublocality = Field()
    config_type = Field()
    platform = Field()
    city = Field()
    listing_date = Field()
    txn_type = Field()
    property_type = Field()
    Building_name = Field()
    lat = Field()
    longt = Field()
    locality = Field()
    sqft = Field()
    Status = Field()
    listing_by = Field() 
    name_lister = Field()
    Selling_price = Field()
    Monthly_Rent = Field()
    Details = Field()
    data_id = Field()
    
