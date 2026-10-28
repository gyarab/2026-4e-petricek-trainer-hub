# TrainerHub

Webová aplikace pro trenéry a jejich klienty (Python, Django, JavaScript, SQL).

## Spuštění (Windows, PowerShell)

```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations accounts
python manage.py makemigrations exercises
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Administrace: http://127.0.0.1:8000/admin/

Trenéři mohou spravovat vlastní cviky a používat sdílené cviky na stránce
`/exercises/`. Sdílené cviky lze vytvořit v administraci bez vyplnění pole
„created by“.
