Quick start
^^^^^^^^^^^
To get the bot up and running immediately, you have to do the following:

1. pip install twitchat (or python -m pip install twitchat if that doesn't work for you)
2. Create a directory for the bot
3.  Inside this directory, run twitchat-settings

Here, you will have to enter the following:

1. The name of your bot account
2. A client ID for that account
3. A corresponding oauth token (This can easily be acquired from here; exclude the "oauth:" part)
4. The channel you want the bot to connect to

If you don't know what any of this means, I have a guide prepared for you.

Finally, create a script in the bot directory (or just run python):::

    from twitchat.twitchbot import main
    main()

Your bot should now be connecting to your Twitch chat and saying "I am here now :)". Try using !ping to see him reply!
