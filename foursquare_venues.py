import yaml
import requests
import datetime
import time
import csv

# Get all Venue IDs for venues within the bounding box.


with open("/Users/irinanazarchuk/Desktop/task/config.yaml", "r") as f:
    cfg = yaml.load(f)

search_params = {
    'client_id': cfg['client_id'],
    'client_secret': cfg['client_secret'],
    'intent': 'checkin',
    'v': '20180218',
    'radius': 2000,
    'limit': 100,
    # 'categoryId': '52f2ab2ebcbc57f1066b8b46',
    'categoryId': '4bf58dd8d48988d1f9941735'
    # 'near': 'Kyiv',
    # 'query': 'Silpo'
}

venue_ids = set()


search_params.update({'ll': '{},{}'.format('50.17617601969889', '30.31628476557327')})

r = requests.get('https://api.foursquare.com/v2/venues/search',
                         params=search_params)
# r = requests.get('https://api.foursquare.com/v2/venues/explore',
#                          params=search_params)

if 'venues' in r.json()['response']:
    venues = r.json()['response']['venues']

    for venue in venues:
        venue_ids.add(venue['id'])

print('{} Unique Venues Scraped: {}.'.format(
      len(venue_ids), datetime.datetime.now()))

# print(r.content)


# Get and process the data for each unique Venue.

venue_params = {
    'client_id': cfg['client_id'],
    'client_secret': cfg['client_secret'],
    'v': '20180218'
}

venue_ids_list = list(venue_ids)   # cannot iterate a set, so must coerce list
venue_count = 0

with open('data/new.csv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'categories', 'lat', 'long', 'num_checkins',
                     'num_likes', 'price', 'rating',
                     'num_ratings', 'url_venue', 'url_foursquare'])

    for venue_id in venue_ids_list:
        r = requests.get(
            'https://api.foursquare.com/v2/venues/{}'.format(venue_id),
            params=venue_params)
        # print(r.content)
        if 'venue' in r.json()['response']:
            venue = r.json()['response']['venue']
            id = venue_id
            name = venue.get('name', '')
            lat = venue.get('location', {}).get('lat', '')
            long = venue.get('location', {}).get('lng', '')
            num_checkins = venue.get('stats', {}).get('checkinsCount', '')
            num_likes = venue.get('likes', {}).get('count', '')
            rating = venue.get('rating', '')
            num_ratings = venue.get('ratingSignals', '')
            price = venue.get('price', {}).get('tier')
            url_venue = venue.get('url', '')
            url_foursquare = venue.get('shortUrl', '')

            # categories is an empty list if there are none.
            categories = venue.get('categories', '')
            if len(categories) == 0:
                categories = ''
            else:
                categories = ', '.join([x['name'] for x in categories])

            writer.writerow([id, name, categories, lat, long, num_checkins,
                             num_likes, price, rating,
                             num_ratings, url_venue, url_foursquare])

        venue_count += 1

        if venue_count % 1000 == 0:
            print('{} Retrieved: {}'.format(venue_count,
                                            datetime.datetime.now()))

        # the venues/* endpoint has a rate limit of 5000 requests/hr
        if venue_count % 5000 == 0:
            time.sleep(60*60)

        time.sleep(0.1)
