from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import OperationalError
from app.db import SessionLocal, engine, get_db
from app.main import app
from app.models import Listing, Reservation, utcnow


def create(client, payload):
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def reserve(client, listing_id, quantity=1):
    return client.post(f'/api/listings/{listing_id}/reservations', json={'customer':'Alex', 'quantity':quantity})


def expire(listing_id):
    with SessionLocal() as db:
        item=db.get(Listing,listing_id)
        item.pickup_start=utcnow()-timedelta(hours=2)
        item.pickup_end=utcnow()-timedelta(seconds=1)
        db.commit()


def test_migrations_and_health(client):
    assert {'listings','reservations','tickets'}.issubset(inspect(engine).get_table_names())
    assert client.get('/health').json()=={'status':'UP'}
    assert client.get('/ready').json()=={'status':'READY'}
    assert client.get('/').json()['service']=='LastBite API'


def test_crud(client,payload):
    item=create(client,payload)
    assert item['quantity_available']==5 and item['state']=='AVAILABLE'
    assert item['discount_percent']==67
    path=f"/api/listings/{item['id']}"
    assert client.get(path).json()['title']==payload['title']
    changed=client.put(path,json={**payload,'title':'New supper','quantity_total':8})
    assert changed.status_code==200 and changed.json()['quantity_available']==8
    assert client.delete(path).status_code==204
    assert client.get(path).status_code==404


@pytest.mark.parametrize('change',[{'title':' '},{'quantity_total':0},{'quantity_total':True},{'price_paise':0},{'price_paise':29901},{'category':'TICKETS'},{'dietary':'UNKNOWN'},{'unexpected':1},{'address':''},{'quantity_total':1.5}])
def test_listing_validation(client,payload,change):
    assert client.post('/api/listings',json={**payload,**change}).status_code==422


def test_invalid_times(client,payload):
    for change in [{'pickup_end':payload['pickup_start']},{'pickup_end':(utcnow()-timedelta(minutes=1)).isoformat()}, {'pickup_start':'2026-10-16T12:00:00'}]:
        assert client.post('/api/listings',json={**payload,**change}).status_code==422


def test_search_filters_and_pagination(client,payload):
    first=create(client,{**payload,'title':'100% rescue','category':'BAKERY','dietary':'VEGAN'})
    create(client,{**payload,'title':'Other meal'})
    create(client,{**payload,'title':'Paused meal','status':'PAUSED'})
    found=client.get('/api/listings?q=%25&category=BAKERY&dietary=VEGAN').json()
    assert found['total']==1 and found['items'][0]['id']==first['id']
    assert client.get('/api/listings?state=AVAILABLE').json()['total']==2
    assert client.get('/api/listings?state=PAUSED').json()['total']==1
    assert len(client.get('/api/listings?limit=1&offset=1').json()['items'])==1
    assert client.get('/api/listings?state=INVALID').status_code==422
    assert client.get('/api/listings?limit=101').status_code==422


def test_reservation_stock_and_snapshot(client,payload):
    item=create(client,payload)
    r=reserve(client,item['id'],2)
    assert r.status_code==201
    assert r.json()['total_paise']==19800 and len(r.json()['pickup_code'])==8
    assert client.get(f"/api/listings/{item['id']}").json()['quantity_available']==3
    assert client.get('/api/stats').json()['meals_rescued']==0
    assert client.get('/api/stats').json()['awaiting_pickup']==2
    assert client.get('/api/reservations').json()[0]['customer']=='Alex'


def test_overselling_is_rejected(client,payload):
    item=create(client,{**payload,'quantity_total':1})
    assert reserve(client,item['id']).status_code==201
    assert reserve(client,item['id']).status_code==409
    assert client.get(f"/api/listings/{item['id']}").json()['state']=='SOLD_OUT'
    assert client.get('/api/listings?state=SOLD_OUT').json()['total']==1


def test_concurrent_reservations_do_not_oversell(client,payload):
    item=create(client,{**payload,'quantity_total':3})
    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses=list(pool.map(lambda _:reserve(client,item['id']).status_code,range(8)))
    assert statuses.count(201)==3 and statuses.count(409)==5
    assert client.get(f"/api/listings/{item['id']}").json()['quantity_available']==0
    assert len(client.get('/api/reservations').json())==3


def test_cancel_restores_stock_once(client,payload):
    item=create(client,payload)
    r=reserve(client,item['id'],2).json()
    path=f"/api/reservations/{r['id']}/cancel"
    assert client.post(path).json()['status']=='CANCELLED'
    assert client.post(path).status_code==409
    assert client.get(f"/api/listings/{item['id']}").json()['quantity_available']==5
    assert client.get('/api/stats').json()['awaiting_pickup']==0


def test_concurrent_cancel_does_not_duplicate_stock(client,payload):
    item=create(client,payload)
    r=reserve(client,item['id'],2).json()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:client.post(f"/api/reservations/{r['id']}/cancel").status_code,range(2)))
    assert sorted(results)==[200,409]
    assert client.get(f"/api/listings/{item['id']}").json()['quantity_available']==5


def test_pickup_code_and_rescued_statistics(client,payload):
    item=create(client,payload)
    r=reserve(client,item['id'],2).json()
    path=f"/api/reservations/{r['id']}/pickup"
    assert client.post(path,json={'pickup_code':'WRONG'}).status_code==422
    result=client.post(path,json={'pickup_code':r['pickup_code'].lower()})
    assert result.status_code==200 and result.json()['picked_up_at']
    assert client.post(path,json={'pickup_code':r['pickup_code']}).status_code==409
    assert client.post(f"/api/reservations/{r['id']}/cancel").status_code==409
    stats=client.get('/api/stats').json()
    assert stats['meals_rescued']==2 and stats['savings_paise']==40000 and stats['boxes_available']==3


def test_pickup_before_window_rejected(client,payload):
    item=create(client,{**payload,'pickup_start':(utcnow()+timedelta(hours=1)).isoformat()})
    r=reserve(client,item['id']).json()
    assert client.post(f"/api/reservations/{r['id']}/pickup",json={'pickup_code':r['pickup_code']}).status_code==409


def test_expiry_is_enforced_without_background_job(client,payload):
    item=create(client,payload)
    r=reserve(client,item['id']).json()
    expire(item['id'])
    assert client.get(f"/api/listings/{item['id']}").json()['state']=='EXPIRED'
    assert reserve(client,item['id']).status_code==409
    assert client.post(f"/api/reservations/{r['id']}/cancel").status_code==409
    assert client.post(f"/api/reservations/{r['id']}/pickup",json={'pickup_code':r['pickup_code']}).status_code==409
    assert client.get('/api/reservations').json()[0]['status']=='EXPIRED'
    assert client.get('/api/listings?state=AVAILABLE').json()['total']==0
    stats=client.get('/api/stats').json()
    assert stats['awaiting_pickup']==stats['boxes_available']==stats['meals_rescued']==0
    assert client.put(f"/api/listings/{item['id']}",json=payload).status_code==409


def test_paused_listing_rejects_new_reservations_but_allows_pickup(client,payload):
    item=create(client,payload)
    r=reserve(client,item['id']).json()
    assert client.put(f"/api/listings/{item['id']}",json={**payload,'status':'PAUSED'}).status_code==200
    assert reserve(client,item['id']).status_code==409
    assert client.post(f"/api/reservations/{r['id']}/pickup",json={'pickup_code':r['pickup_code']}).status_code==200


def test_reservation_history_and_promises_protected(client,payload):
    item=create(client,payload)
    reserve(client,item['id'],2)
    path=f"/api/listings/{item['id']}"
    assert client.delete(path).status_code==409
    assert client.put(path,json={**payload,'quantity_total':1}).status_code==409
    for change in [{'price_paise':10000},{'pickup_end':(utcnow()+timedelta(hours=3)).isoformat()},{'allergens':'None'}]:
        assert client.put(path,json={**payload,**change}).status_code==409
    result=client.put(path,json={**payload,'quantity_total':7})
    assert result.status_code==200 and result.json()['quantity_available']==5


@pytest.mark.parametrize('quantity',[0,-1,21,1.5,True])
def test_reservation_validation(client,payload,quantity):
    item=create(client,payload)
    assert reserve(client,item['id'],quantity).status_code==422
    assert client.get(f"/api/listings/{item['id']}").json()['quantity_available']==5


def test_missing_resources(client,payload):
    assert client.get('/api/listings/99999').status_code==404
    assert reserve(client,99999).status_code==404
    assert client.post('/api/reservations/99999/cancel').status_code==404
    assert client.delete('/api/listings/99999').status_code==404


def test_readiness_failure_does_not_break_liveness(client):
    class BrokenDB:
        def execute(self,*args):
            raise OperationalError('read',{},Exception('offline'))
    app.dependency_overrides[get_db]=lambda:BrokenDB()
    try:
        assert client.get('/ready').status_code==503
        assert client.get('/health').status_code==200
    finally:
        app.dependency_overrides.clear()


def test_metrics_use_route_templates(client,payload):
    item=create(client,payload)
    client.get(f"/api/listings/{item['id']}")
    client.get('/unknown-test-path')
    metrics=client.get('/metrics').text
    assert 'lastbite_http_requests_total' in metrics
    assert 'route="/api/listings/{listing_id}"' in metrics
    assert 'route="unmatched"' in metrics
    assert 'route="/unknown-test-path"' not in metrics
