# Mastodon Secure Feed

Mastodon Secure Feed is a Python-based application that securely fetches the latest posts from a Mastodon account and serves them via an API. This application uses environment variables to securely store Mastodon credentials and cache data to minimize API calls.

## Features

- Securely fetch and serve Mastodon posts
- Caching mechanism to reduce API calls
- Easily deployable with Gunicorn and Nginx
- Configurable via environment variables

## Prerequisites

- Python 3.x
- Pip
- Virtualenv (optional but recommended)
- Gunicorn
- Nginx
- Certbot (for SSL certificates)

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://git.vdm.dev/Llewellyn/mastodon-secure-feed.git
    cd mastodon-secure-feed
    ```

2. **Create and activate a virtual environment** (optional but recommended):

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root with the following content:

    ```sh
    MASTODON_INSTANCE=https://joomla.social
    ACCESS_TOKEN=your_access_token_here
    ```

## Running the Application

1. **Run the Flask application locally**:

    ```sh
    export FLASK_APP=src/app.py
    export FLASK_ENV=development
    flask run
    ```

## Deploying with Gunicorn and Nginx

### Step 4: Set Up Gunicorn

If the Flask app works as expected, you can now configure Gunicorn to serve your app. Create a simple Gunicorn config file or just run Gunicorn with the necessary parameters:

```sh
gunicorn --bind 0.0.0.0:8000 src.app:app
```

### Step 5: Create a Systemd Service File for Gunicorn

To keep Gunicorn running, create a systemd service file:

```sh
sudo systemctl edit --force --full mastodon_secure_feed.service
```

Paste in the following:

```ini
[Unit]
Description=Gunicorn instance to serve mastodon-secure-feed
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/mastodon-secure-feed
Environment="PATH=/home/ubuntu/mastodon-secure-feed/venv/bin"
ExecStart=/home/ubuntu/mastodon-secure-feed/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/mastodon-secure-feed/mastodon_secure_feed.sock -m 007 src.app:app

[Install]
WantedBy=multi-user.target
```

Start and enable the Gunicorn service:

```sh
sudo systemctl start mastodon_secure_feed
sudo systemctl enable mastodon_secure_feed
```

### Step 6: Configure Nginx

Add a new server block to your Nginx configuration or edit an existing one:

```sh
sudo nano /etc/nginx/sites-available/default
```

Add this server block:

```nginx
# HTTPS server block for yourdomain.com
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/mastodon-secure-feed/mastodon_secure_feed.sock;
    }

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com;

    location / {
        return 301 https://$host$request_uri;
    }
}
```

Test the configuration and restart Nginx:

```sh
sudo nginx -t
sudo systemctl restart nginx
```

## Usage

1. **Fetching Latest Posts**:

    Make a GET request to the `/statuses` endpoint to fetch the latest cached posts:

    ```sh
    curl http://yourdomain.com/statuses?limit=4
    ```

    You can also specify the number of posts to fetch using the `limit` parameter (up to a maximum of 10):

    ```sh
    curl http://yourdomain.com/statuses?limit=4
    ```

2. **Updating Cache via Webhook**:

    Trigger a cache update by making a GET request to the `/webhook` endpoint:

    ```sh
    curl http://yourdomain.com/webhook
    ```

    You can also specify the number of posts to fetch using the `limit` parameter (up to a maximum of 10):

    ```sh
    curl http://yourdomain.com/webhook?limit=4
    ```

## Using the JavaScript Widget to Display the API Result

To display the Mastodon feed on your website, you can use the `mastodon-feed-display` JavaScript widget. This widget fetches the latest posts from the `mastodon-secure-feed` API and displays them.

For more information and setup instructions, visit the [mastodon-feed-display repository](https://git.vdm.dev/Llewellyn/mastodon-feed-display).

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Create a new Pull Request

## License

This project is licensed under the GNU General Public License v2.0 - see the LICENSE file for details.
