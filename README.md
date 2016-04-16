# StockTwits Server

## Dependency

Install dependency to your computer ,
```
    git clone https://github.com/jckhang/stockTwits_server
    cd stockTwits_server
    virtualenv venv
    source venv/bin/source
    pip install -r requirements.txt
```
## Run the server local

Run in terminal
```
    python app.py
```
and open http://127.0.0.1:5000/ in the browser.

## Deploy to Heroku

Run in terminal
```
    heroku login
    heroku git:remote -a stockbackend
```

After you edition of the codes,

```
    git add .
    git commit -m 'Some message'
    git push heroku master
    heroku open
```