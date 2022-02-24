# Twitter_Sentiment_REST-Api

ssh -i "twitter-sentiment.pem" ec2-user@ec2-35-154-98-182.ap-south-1.compute.amazonaws.com

sudo apt-get update

sudo apt install pip -y

sudo apt install git -y

git clone https://github.com/nikitperiwal/Twitter-Sentiment-REST-Api.git

sudo apt install nginx -y

cd /etc/nginx/sites-enabled/

sudo nano fastapi_nginx

server {
    listen 80;
    server_name 13.127.87.240;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}

sudo service nginx restart

cd ~/Twitter-Sentiment-REST-Api/

pip3 install -r requirements.txt

python3 -m uvicorn app:app
