Thank you for providing those details. That's very helpful.

You've mentioned that in your API key settings, "API restrictions" is set to "Restrict key". This is a very likely cause of the problem.

If you restrict the API key, you must explicitly allow it to be used with the **Identity Toolkit API**, which is what Firebase Authentication uses behind the scenes.

Here's how to fix it:

1.  **Go to the Google Cloud Console:** Open **APIs & Services > Credentials**.
2.  **Select your API key:** Click on the name of the API key you are using.
3.  **Under "API restrictions,"** you should see a dropdown menu.
4.  **Select "Identity Toolkit API"** from the list and make sure it is checked. If it's not in the list, you may need to enable the "Identity Toolkit API" for your project first.
5.  **Save your changes.**

After you've done this, please try to log in with a real phone number again. This should resolve the `auth/invalid-app-credential` error.