# scraper-docker

Dockerized the scraper. The sample script is going to extract data from Redfin.

# How to run

```bash
cd /your/script/directory
docker run -it -w /usr/workspace -v $(pwd):/usr/workspace jjjjjia11/scraper-docker bash
```
Sample Run app.py

```bash
python3 app.py
```
