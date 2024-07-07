import requests
import json
import time
import schedule

# Linode API URL and authentication token
linode_api_url = 'https://api.linode.com/v4/account/logins'
bearer_token = '[YOUR_LINODE_API_TOKEN]'

# Slack Webhook URL
slack_webhook_url = 'https://hooks.slack.com/services/[YOUR_SLACK_CHANNEL_URL]'

# Variable to store the last ID since the last call
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

    # Filter the changed entries
    new_logins = [login for login in login_data['data'] if login['id'] > last_id]
    if new_logins:
        last_id = max(login['id'] for login in new_logins)

        # Create message to send to Slack
        message = "*Linode Login Attempts:*\n"
        for login in new_logins:
            message += f"ID: {login['id']}\n"
            message += f"Datetime: {login['datetime']}\n"
            message += f"IP: {login['ip']}\n"
            message += f"Username: {login['username']}\n"
            message += f"Status: {login['status']}\n"
            message += f"Restricted: {login['restricted']}\n"
            message += "\n"
        # Add a separator line at the end of the message
        message += "-----------------------------\n"

        # Send Slack message
        slack_message = {
            "text": message
        }

        response = requests.post(slack_webhook_url, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            print('Message posted successfully.')
        else:
            print(f'Failed to post message. Status code: {response.status_code}')

# Execute fetch_and_send_logins function every 30 seconds
schedule.every(30).seconds.do(fetch_and_send_logins)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
