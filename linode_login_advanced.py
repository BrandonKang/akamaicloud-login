import requests
import json
import time
import schedule

# Linode API URL and authentication token
linode_api_url = 'https://api.linode.com/v4/account/logins'
bearer_token = '[YOUR_LINODE_API_TOKEN]'

# Slack Webhook URL
slack_webhook_url = 'https://hooks.slack.com/services/[YOUR_SLACK_WEBHOOK_URL]'

# Variable to store the last processed ID
last_id = 0

def fetch_and_send_logins():
    global last_id

    # Call Linode API
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(linode_api_url, headers=headers)
    login_data = response.json()

    # Filter new logins
    new_logins = [login for login in login_data['data'] if login['id'] > last_id]
    if new_logins:
        last_id = max(login['id'] for login in new_logins)

        # Create Slack attachment message
        attachments = []
        for login in new_logins:
            color = "good" if login['status'] == "successful" else "danger"
            attachments.append({
                "color": color,
                "fields": [
                    {
                        "title": "ID",
                        "value": login['id'],
                        "short": True
                    },
                    {
                        "title": "Datetime",
                        "value": login['datetime'],
                        "short": True
                    },
                    {
                        "title": "IP",
                        "value": login['ip'],
                        "short": True
                    },
                    {
                        "title": "Username",
                        "value": login['username'],
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": login['status'],
                        "short": True
                    },
                    {
                        "title": "Restricted",
                        "value": str(login['restricted']),
                        "short": True
                    }
                ]
            })

        slack_message = {
            "attachments": attachments
        }

        response = requests.post(slack_webhook_url, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            print('Message posted successfully.')
        else:
            print(f'Failed to post message. Status code: {response.status_code}')
            try:
                print(response.json())
            except json.JSONDecodeError:
                print(response.text)

# Run fetch_and_send_logins function every 30 seconds
schedule.every(30).seconds.do(fetch_and_send_logins)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)