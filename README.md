# Calls records
Application that receives call detail records and calculates monthly bills for a given telephone number.

## Environment setup
#### Using docker
If you have `docker` and `docker-compose`, you can get up and running in a few steps:
```
docker-compose build
docker-compose run --rm web ./manage.py migrate
docker-compose up
```

The tests suite uses `pytest`. Instantiate a temporary `docker` container to run them:
```
docker-compose run --rm web pytest
```
#### Manually
This project requires `Python 3.6` and `pipenv` to be installed. The setup should work with this:
```
pip install pipenv
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

Either setting up manually or using `docker`, the server should run on [http://localhost:8000](http://localhost:8000).  
## Application API
You can preview and interact with the API at: [http://localhost:8000/docs/](http://localhost:8000/docs/).  
Summary of the endpoints:
### POST /records/
Creates a new call record. This endpoint accepts both `start` and `end` records.
+ body:

        {
            "type":  // Indicate if it's a call "start" or "end" record;
            "timestamp":  // The timestamp of when the event occured;
            "call_id":  // Unique for each call record pair;
            "source":  // The subscriber phone number that originated the call;
            "destination":  // The phone number receiving the call.
        }
  + example of starting call:
   ```
   curl -X POST http://localhost:8000/records/ -H 'Content-Type: application/json' -d '{
      "type":  "start",
      "timestamp": "2018-03-20T21:57:13Z",
      "call_id":  "asdqwe",
      "source":  "11988776655",
      "destination":  "11944332211"
  }'
  ```
  + example of ending call:
   ```      
  curl -X POST http://localhost:8000/records/ -H 'Content-Type: application/json' -d '{
      "type":  "end",
      "timestamp": "2018-03-20T22:12:56Z",
      "call_id":  "asdqwe"
  }'
  ```
+ Response 201 (application/json). E.g.:
         
        {
            "id": 78,
            "call_id": "asdqwe",
            "started_at": "2018-03-20T21:57:13Z",
            "ended_at": "2018-03-20T22:12:56Z",
            "source": "11988776655",
            "destination": "11944332211",
            "duration": "00:15:43",
            "price": "0.54"
        }

### GET /records/<call_id>/
Retrieves a call record using its `call_id`.
+ Parameters
  + call_id: (required) string - The unique identifier of the record pair
+ example of retrieval:
    ```
    curl -X GET http://localhost:8000/records/asdqwe/
    ```
+ Response 200 (application/json). E.g.:
         
        {
            "id": 78,
            "call_id": "asdqwe",
            "started_at": "2018-03-20T21:57:13Z",
            "ended_at": "2018-03-20T22:12:56Z",
            "source": "11988776655",
            "destination": "11944332211",
            "duration": "00:15:43",
            "price": "0.54"
        }

### GET /bills/\<phone>/\<month-year>/
Retrieves the monhly bill for a given `phone` number.
+ Parameters
  + phone: (required) number in `AAXXXXXXXXX` format - The source number of the calls
  + month-year: (optional) date in `MM-YYYY` format - Dash-separated month and year of the bills 
+ example of retrieval:
    ```
    curl -X GET http://localhost:8000/bills/11988776655/
    ```
    or
    ```
    curl -X GET http://localhost:8000/bills/11988776655/01-2018/
    ```
+ Response 200 (application/json). E.g.:
         
        [
            {
                "started_at": "2018-02-10T11:57:13Z",
                "ended_at": "2018-02-10T17:37:13Z",
                "destination": "11911223344",
                "duration": "05:40:00",
                "price": "30.96"
            },
            {
                "started_at": "2018-02-20T21:57:13Z",
                "ended_at": "2018-02-20T22:12:56Z",
                "destination": "11944332211",
                "duration": "00:15:43",
                "price": "0.54"
            }
        ]
