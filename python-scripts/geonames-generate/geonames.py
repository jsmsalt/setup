from peewee import *
import uuid

mysql_db = MySQLDatabase('geonames', user='root', password='root',
                         host='127.0.0.1')

mysql_db_2 = MySQLDatabase('eroted', user='root', password='root',
                         host='127.0.0.1')

class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = mysql_db

class BaseModelTwo(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = mysql_db_2

class Geoname(BaseModel):
    geonameid = IntegerField(primary_key = True)
    fclass = CharField()
    name = CharField()
    latitude = DecimalField()
    longitude = DecimalField()
    population = IntegerField()
    timezone = CharField()
    visited = CharField()
    class Meta:
        table_name = 'geoname'

class Hierarchy(BaseModel):
    parentId = IntegerField()
    childId = IntegerField()
    type = CharField()
    class Meta:
        table_name = 'hierarchy'
        primary_key = False


class Name(BaseModel):
    geonameid = IntegerField()
    isoLanguage = CharField()
    alternateName = CharField()
    isPreferredName = SmallIntegerField()
    isShortName = SmallIntegerField()
    isColloquial = SmallIntegerField()
    isHistoric = SmallIntegerField()
    class Meta:
        table_name = 'alternatename'
        primary_key = False

class GeonameName(BaseModelTwo):
    id = BinaryUUIDField(primary_key = True, default=uuid.uuid4)
    geoname_id = BinaryUUIDField()
    language = CharField()
    name = CharField()
    preferred = SmallIntegerField()
    short = SmallIntegerField()
    colloquial = SmallIntegerField()
    historic = SmallIntegerField()
    class Meta:
        table_name = 'geoname_names'

class Country(BaseModelTwo):
    geonameid = IntegerField()
    id = BinaryUUIDField(primary_key = True, default=uuid.uuid4)
    status = CharField()
    class Meta:
        table_name = 'countries'

class State(BaseModelTwo):
    id = BinaryUUIDField(primary_key = True, default=uuid.uuid4)
    country_id = BinaryUUIDField()
    name = CharField()
    latitude = DecimalField()
    longitude = DecimalField()
    population = IntegerField()
    timezone = CharField()
    geonameid = IntegerField()
    class Meta:
        table_name = 'states'

class Geo(BaseModelTwo):
    id = BinaryUUIDField(primary_key = True, default=uuid.uuid4)
    parent_id = BinaryUUIDField()
    name = CharField()
    latitude = DecimalField()
    longitude = DecimalField()
    population = IntegerField()
    timezone = CharField()
    geonameid = IntegerField()
    class Meta:
        table_name = 'geo_locations'

mysql_db.connect()
mysql_db_2.connect()

# print(Geoname.select().where(Geoname.fclass.in_(['A', 'P'])).where(Geoname.visited == '2').count())

# for c in Country.select():
#     country = Geoname.select().where(Geoname.geonameid == c.geonameid).first()
#     if country != None:
#         exist = Geo.select().where(Geo.geonameid == country.geonameid).first()
#         if exist == None:
#             new_country = Geo.create(
#                 geonameid=country.geonameid,
#                 name=country.name,
#                 latitude=country.latitude,
#                 longitude=country.longitude,
#                 population=country.population,
#                 timezone=country.timezone
#                 )
#             new_country.save()

#             print('new country ', new_country.name)

#             for children_state in Hierarchy.select().where(Hierarchy.parentId == country.geonameid):
#                 state = Geoname.select().where(Geoname.geonameid == children_state.childId).where(Geoname.visited == '0').first()
#                 if state != None:
#                     exist = Geo.select().where(Geo.geonameid == state.geonameid).first()
#                     if exist == None:
#                         new_state = Geo.create(
#                             parent_id=new_country.id,
#                             geonameid=state.geonameid,
#                             name=state.name,
#                             latitude=state.latitude,
#                             longitude=state.longitude,
#                             population=state.population,
#                             timezone=state.timezone
#                             )
#                         new_state.save()

#                         print('new state ', new_state.name)

#                         for children_city in Hierarchy.select().where(Hierarchy.parentId == new_state.geonameid):
#                             city = Geoname.select().where(Geoname.geonameid == children_city.childId).where(Geoname.visited == '0').first()
#                             if city != None:
#                                 exist = Geo.select().where(Geo.geonameid == city.geonameid).first()
#                                 if exist == None:
#                                     new_city = Geo.create(
#                                         parent_id=new_state.id,
#                                         geonameid=city.geonameid,
#                                         name=city.name,
#                                         latitude=city.latitude,
#                                         longitude=city.longitude,
#                                         population=city.population,
#                                         timezone=city.timezone
#                                     )
#                                     new_city.save()

#                                     for children_neighbourhood in Hierarchy.select().where(Hierarchy.parentId == new_city.geonameid):
#                                         neighbourhood = Geoname.select().where(Geoname.geonameid == children_neighbourhood.childId).where(Geoname.visited == '0').first()
#                                         if neighbourhood != None:
#                                             exist = Geo.select().where(Geo.geonameid == neighbourhood.geonameid).first()
#                                             if exist == None:
#                                                 new_neighbourhood = Geo.create(
#                                                     parent_id=new_city.id,
#                                                     geonameid=neighbourhood.geonameid,
#                                                     name=neighbourhood.name,
#                                                     latitude=neighbourhood.latitude,
#                                                     longitude=neighbourhood.longitude,
#                                                     population=neighbourhood.population,
#                                                     timezone=neighbourhood.timezone
#                                                 )
#                                                 new_neighbourhood.save()

#                                                 neighbourhood.visited = '1'
#                                                 neighbourhood.save()
#                                     city.visited = '1'
#                                     city.save()
#                         state.visited = '1'
#                         state.save()







# for geo in Geo.select():
#     for name in Name.select().where(Name.isoLanguage.in_(['es', 'en', 'pt', 'fr', 'it'])).where(Name.geonameid == geo.geonameid):
#         new_name = GeonameName.create(
#             geoname_id=geo.id,
#             language=name.isoLanguage,
#             name=name.alternateName,
#             preferred=name.isPreferredName,
#             short=name.isShortName,
#             colloquial=name.isColloquial,
#             historic=name.isHistoric
#         )
#         new_name.save()


country = Geo.select().where(Geo.name == 'Eswatini').first()

for state in Geo.select().where(Geo.parent_id == country.id):
    for city in Geo.select().where(Geo.parent_id == state.id):
        for neighborhood in Geo.select().where(Geo.parent_id == city.id):
            for other in Geo.select().where(Geo.parent_id == neighborhood.id):
                print('other: ', other.name)
                item = Geo.get(Geo.id == other.id)
                item.delete_instance()
            print('neighborhood: ', neighborhood.name)
            item = Geo.get(Geo.id == neighborhood.id)
            item.delete_instance()
        print('city: ', city.name)
        item = Geo.get(Geo.id == city.id)
        item.delete_instance()
    print('state: ', state.name)
    item = Geo.get(Geo.id == state.id)
    item.delete_instance()
# print('country: ', country.name)
# country.delete_instance()




# for pagina in range(1, 5):
#     for location in Geoname.select().where(Geoname.fclass.in_(['A', 'P'])).where(Geoname.visited == '0').limit(5000):
#         geoid = location.geonameid
#         visited = False

#         cities = City.select().where(City.geonameid == geoid)
#         cities_count = cities.count()

#         if cities_count > 0:
#             visited = True
#         else:
#             states = State.select().where(State.geonameid == geoid)
#             states_count = states.count()
#             if states_count > 0:
#                 visited = True
#             else:
#                 countries = Country.select().where(Country.geonameid == geoid)
#                 countries_count = countries.count()
#                 if countries_count > 0:
#                     visited = True
        
#         if visited == True:
#             location.visited = '1'
#         else:
#             location.visited = '2'
        
#         location.save()

#     print(pagina)