Still working on this project locally

# College Major project

## Email setup (Gmail)

If you see `535 Username and Password not accepted`, configure Gmail like this:

1. Turn on Google 2-Step Verification for the sender account.
2. Generate a Gmail App Password (16 characters).
3. Set `.env` values:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your16charapppassword
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

Notes:
- Use the App Password, not your normal Gmail password.
- If copied with spaces (`xxxx xxxx xxxx xxxx`), spaces are auto-removed in app config.