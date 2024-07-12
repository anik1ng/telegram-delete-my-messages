# telegram-delete-my-messages
Python script for delete / show all your messages or reactions from groups and supergroups.

## Functionality

* Show all your groups or supergroups
* Show all your messages in groups/supergroups
* Show all your reactions in groups/supergroups
* Delete all your messages in selected group/supergroup
* Delete all your reactions in selected group/supergroup


## How to use?

### 1. Get Telegram credentials

* Go to https://my.telegram.org/
* Login
* Click **API development tools**
* Create standalone application
* Copy `App api_id` and `App api_hash`

### 2. Installation

```
git clone git@github.com:anik1ng/telegram-delete-my-messages.git
cd telegram-delete-my-messages
pip install -r requirements.txt
python run.py
```

### 3. Usage

```
python run.py

Enter your Telegram API id: 11223344
Enter your Telegram API hash: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Enter your Telegram phone number (12223334455): 12223334455
Please enter your phone (or bot token): 12223334455
Please enter the code you received: 12345
Signed in successfully as User Name; remember to not break the ToS or you will risk an account ban!

Options:
[1] Supergroups
[2] Groups
[0] Exit
Choose (1, 2 or 0 for exit): 
```

After that, your credentials are stored in the `settings.json` file. If you want to log in to a different account or change your credentials, simply delete the `settings.json` file.


## About and contribution

I created this script to have privacy on telegram. 
It would be very good if such functionality was provided by Telegram itself.

If you have any suggestions, ideas, improvements, please create your own Isue and send me your PR's.
