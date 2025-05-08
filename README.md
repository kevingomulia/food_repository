# Koderpad
An online Python and SQL database playground for testing codes.

## Requirements
1. make
2. Docker
3. Python3.11

## Local Development
1. Setup environment variables.
    ```sh
    cp -i .streamlit/secrets.toml.example .streamlit/secrets.toml
    ```
- Uncomment and set a value for `APP_PWD` in `.streamlit/secrets.toml` to test for password checking, otherwise leave it as it is
- The default value for `DATABASE_URL` in `.streamlit/secrets.toml` should match the `make db` in `Makefile`. Update if required to point to other database url.

2. Run database and app
    ```sh
    $ make db  # run a Postgres db container in the background based on DATABASE_URL in .env
    $ make run # run the Streamlit app
    ```
