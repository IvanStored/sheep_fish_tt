```sh
git clone https://github.com/IvanStored/sheep_fish_tt.git
python -m venv venv
source venv/bin/activate (Linux) or venv\Scripts\activate (Windows)
pip install -r requirements.txt
docker-compose up
python manage.py migrate
python manage.py runserver
celery -A sheepfish_tt worker -l INFO
```
