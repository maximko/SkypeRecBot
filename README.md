Skype Record Bot
================

Skype Record Bot allows you to record Skype calls on server-side.

How to get it working
---------------------

1. Install Skype4Py form https://github.com/mondhs/skype4py (this fork has important bugfixes).
2. Change variables ``fileurl`` and ``files_path`` according to your environment in file **skyperecbot.py**.
  * You may need to prepare your web server.
3. Run Skype.
4. Run ``skyperecordbot.py``
5. Allow bot to use Skype API.
6. See *Usage* below.

Tested with Skype for Linux v2.2.0.35.

Usage
-----

1. Add bot's account to your contact list and send authorization request.
2. Make call to bot or invite it to conference.
3. Receive the link to a record after hanging up.
  * Depending on your ``fileurl`` setting in **skyperecbot.py**

License
-------
WTFPL
