
# heroku pg:pull DATABASE_URL snaccbot -a snacc-bot

if __name__ == "__main__":
    import snacc

    snacc.run()
