# LightOutScheduler

LightOutScheduler is a script designed to determine power outage times from Telegram for a specific queue (in this example, Queue 4). It adds this time to Crontab to shut down all necessary servers 10 minutes before the outage using a script.

## Features

- **Power Outage Time Detection**: Automatically retrieves power outage times for a specified queue from Telegram.
- **Crontab Scheduling**: Adds the outage time to Crontab to schedule server shutdowns.
- **Server Shutdown**: Shuts down all necessary servers 10 minutes before the scheduled outage to prevent data loss and hardware damage.
- **Logging**: Logs all activities and actions taken by the script.
- **Telegram Notifications**: Sends notifications to a specified Telegram chat about the status and actions taken.

## Requirements

- **Bash**: Ensure you have a Bash shell environment.
- **Curl**: Required for making API requests.
- **JQ**: Command-line JSON processor.
- **Telegram Bot**: Ensure you have a Telegram bot set up to receive power outage times.

## Installation

1. **Clone the Repository**:

    ```sh
    git clone https://github.com/your-username/LightOutScheduler.git
    cd LightOutScheduler
    ```

2. **Create Configuration File**:

    Create a file named `config.sh` and add your Telegram bot token and chat ID:

    ```sh
    TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
    CHAT_ID="your-telegram-chat-id"
    QUEUE="4"
    ```

3. **Make the Script Executable**:

    ```sh
    chmod +x lightout_scheduler.sh
    ```

## Usage

Run the script manually to check for power outage times and update the Crontab:

```sh
./lightout_scheduler.sh
