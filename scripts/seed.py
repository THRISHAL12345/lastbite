#!/usr/bin/env python3
"""Add fictional LastBite kitchens to an empty demo database."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from urllib.request import Request, urlopen

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:8000')
args=parser.parse_args()
base=args.url.rstrip('/')
def request(path,body=None):
    req=Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
    with urlopen(req,timeout=15) as response:return json.load(response)
if request('/api/listings?limit=1')['total']:
    raise SystemExit('Listings already exist; no demo data added.')
now=datetime.now(timezone.utc)
boxes=[
 ('The sunset supper box','The Green Table','MEALS','VEGETARIAN','A comforting bowl of dal, fragrant rice, two rotis and seasonal vegetables. One generous meal.',9900,29900,8,3,'Milk, wheat','12 Market Lane, Jubilee Hills'),
 ('A very good bread day','Loaf & Found','BAKERY','VEGETARIAN','Buttery croissants, sourdough slices and a little something sweet. Baked today, loved tonight.',12900,39900,5,2,'Wheat, milk, eggs','7 Baker Street, Banjara Hills'),
 ('The garden party','Roots Collective','PRODUCE','VEGAN','A colourful selection of seasonal vegetables and fresh fruit. Perfectly good, perfectly imperfect.',7900,24900,6,4,'Ask the kitchen','24 Garden Road, Gachibowli'),
 ('Sweet little plot twist','Midnight Crumb','DESSERTS','VEGETARIAN','A surprise duo of chocolate cake and a bakery favourite. The best kind of happy ending.',14900,45000,4,2.5,'Milk, eggs, wheat, nuts','18 Crescent Lane, Madhapur'),
 ('Curry up & rescue','Spice Story','MEALS','VEGETARIAN','A freshly prepared vegetarian curry with jeera rice and warm flatbread. Big flavour, small footprint.',11900,34900,7,3.5,'Milk, wheat','9 Spice Market, Kondapur'),
 ('The golden hour bag','Butter Days','BAKERY','VEGETARIAN','Flaky pastries and soft dinner rolls from our last bake of the day. A little box of sunshine.',8900,27900,3,1.5,'Wheat, milk, eggs','3 Sunrise Avenue, Hitech City'),
]
ids=[]
for title,kitchen,category,dietary,description,price,original,stock,hours,allergens,address in boxes:
    item=request('/api/listings',dict(title=title,restaurant=kitchen,category=category,dietary=dietary,description=description,price_paise=price,original_price_paise=original,quantity_total=stock,pickup_start=(now-timedelta(minutes=15)).isoformat(),pickup_end=(now+timedelta(hours=hours)).isoformat(),allergens=allergens,address=address))
    ids.append(item['id'])
    print(f"Published LB-{item['id']}: {title}")
# Impact cards reflect real persisted demo pickups, not hard-coded dashboard numbers.
for listing_id,quantity in [(ids[0],3),(ids[1],3),(ids[2],2)]:
    r=request(f'/api/listings/{listing_id}/reservations',{'customer':'Fictional demo pickup','quantity':quantity})
    request(f"/api/reservations/{r['id']}/pickup",{'pickup_code':r['pickup_code']})
request(f'/api/listings/{ids[3]}/reservations',{'customer':'Alex (demo)','quantity':2})
print('Seeded six fictional kitchens, eight collected meals, and one pending reservation.')
