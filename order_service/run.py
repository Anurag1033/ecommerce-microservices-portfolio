from src import create_app

app = create_app()

if __name__ == '__main__':
    # Runs on port 5001 locally so it doesn't conflict with the Inventory service later
    app.run(host='0.0.0.0', port=5001, debug=True)