from empty_room import app


def main():
    # app.run(host='0.0.0.0', port='9999', debug=False, ssl_context=("./cert/4075081_dev.mylwx.cn.pem", "./cert/4075081_dev.mylwx.cn.key"))
    app.run(host='0.0.0.0', port='9999', debug=False)

if __name__ == "__main__":
    main()
